from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.initiative import InitiativeCreate, InitiativeUpdate, InitiativeResponse
from app.crud import initiative as crud_initiative
from app.db.session import get_db
from app.api.dependencies import get_current_user, get_current_user_with_workspace
from app.crud import user as user_crud
from jose import jwt, JWTError
from app.core.config import settings
from app.models.teams import TeamMember

router = APIRouter()

def _extract_email(current_user: dict) -> Optional[str]:
    if not isinstance(current_user, dict):
        return None
    if current_user.get("email"):
        return current_user["email"]
    access_token = current_user.get("accessToken")
    if isinstance(access_token, str):
        try:
            nested_payload = jwt.decode(
                access_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            return nested_payload.get("email")
        except JWTError:
            return None
    return None

@router.post("/initiatives", response_model=InitiativeResponse)
def create_initiative_api(initiative: InitiativeCreate, 
                          db: Session = Depends(get_db),
                          current_user: dict = Depends(get_current_user)):
    """API endpoint to create a new initiative."""
    print(f"current_user: {current_user}")
    email = _extract_email(current_user)
    if not email:
        raise HTTPException(status_code=401, detail="User email missing from token")
    user = user_crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return crud_initiative.create_initiative(db=db, initiative=initiative)

@router.patch("/initiatives/{initiative_id}", response_model=InitiativeResponse)
def update_initiative(initiative_id: str, initiative: InitiativeUpdate, 
                      db: Session = Depends(get_db),
                      current_user: dict = Depends(get_current_user)):
    email = _extract_email(current_user)
    if not email:
        raise HTTPException(status_code=401, detail="User email missing from token")
    user = user_crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return crud_initiative.update_initiative(db=db, initiative_id=initiative_id, initiative=initiative)

@router.get("/initiatives", response_model=list[InitiativeResponse])
def list_initiatives_api(
    db: Session = Depends(get_db),
    teams: Optional[List[str]] = Query(None),  # Optional list of team IDs
    owners: Optional[List[str]] = Query(None),  # Optional owner ID
    status: Optional[str] = Query(None),  # Optional status
    member_id: Optional[str] = Query(None),  # Optional: filter initiatives visible to this member
    workspace_id: Optional[str] = Query(None),  # Optional workspace filter
    team_id: Optional[str] = Query(None),  # New: explicit team_id for team-member visibility
    user_context: dict = Depends(get_current_user_with_workspace)
):
    """API endpoint to list initiatives visible to a member, scoped to tenant/workspace.

    Defaults to the current user's visibility (member_id = current user). Team and owner filters are ignored when member_id is used.
    """
    # If explicit team_id is provided, enforce team-member visibility rules.
    if team_id:
        # Verify requester is a member of the team
        is_member = (
            db.query(TeamMember)
            .filter(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_context["user"].user_id,
            )
            .first()
            is not None
        )
        if not is_member:
            raise HTTPException(status_code=403, detail="Not a member of the requested team")

        # Force filtering by this team and ignore owners/member gating
        return crud_initiative.get_all_initiatives(
            db=db,
            teams=[team_id],
            owners=None,
            status=status,
            workspace_id=workspace_id or user_context["workspace_id"],
            member_id=None,
        )

    # Visibility rules when no explicit team_id:
    # - If teams are specified, return all initiatives under those teams for the workspace/tenant,
    #   regardless of owner/DRI. This ensures everyone in the team can see initiatives of their team.
    # - Otherwise, default to the current user's visibility (member_id), which restricts to teams
    #   that the member belongs to.
    if teams and len(teams) > 0:
        # When teams filter is present, just return initiatives for those teams
        # No member visibility checks - just return all initiatives associated with the team
        return crud_initiative.get_all_initiatives(
            db=db, 
            teams=teams,
            owners=None,  # Ignore owner filters when filtering by teams
            status=status,
            workspace_id=workspace_id or user_context["workspace_id"],
            member_id=None  # No member visibility when filtering by teams
        )
    else:
        # Default to current user's visibility (member_id), which includes teammate-owned initiatives
        effective_member_id = member_id or user_context["user"].user_id
        return crud_initiative.get_all_initiatives(
            db=db, 
            teams=teams,
            owners=owners if not effective_member_id else None,
            status=status,
            workspace_id=workspace_id or user_context["workspace_id"],
            member_id=effective_member_id
        )

@router.get("/initiatives/{initiative_id}", response_model=InitiativeResponse)
def get_initiative(initiative_id: str, 
                    db: Session = Depends(get_db),
                    current_user: dict = Depends(get_current_user),
                    team_id: Optional[str] = Query(None)):
    """Get a specific initiative by ID"""
    email = _extract_email(current_user)
    if not email:
        raise HTTPException(status_code=401, detail="User email missing from token")
    user = user_crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    # If team_id is provided, allow access if the requester is a member of that team
    if team_id:
        from app.models.initiative import Initiative as InitiativeModel
        from app.models.initiative_teams import initiative_teams
        from sqlalchemy import and_

        # Check membership
        is_member = (
            db.query(TeamMember)
            .filter(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user.user_id,
            )
            .first()
            is not None
        )
        if not is_member:
            raise HTTPException(status_code=403, detail="Not a member of the requested team")

        # Verify the initiative is associated with the team
        linked = (
            db.query(InitiativeModel.initiative_id)
            .join(initiative_teams, initiative_teams.c.initiative_id == InitiativeModel.initiative_id)
            .filter(
                and_(
                    InitiativeModel.initiative_id == initiative_id,
                    initiative_teams.c.team_id == team_id,
                )
            )
            .first()
            is not None
        )
        if not linked:
            raise HTTPException(status_code=404, detail="Initiative not linked to the requested team")

    return crud_initiative.get_initiative(db, initiative_id=initiative_id)


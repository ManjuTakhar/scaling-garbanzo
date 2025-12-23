from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.teams import (
    TeamCreate,
    TeamResponse,
    TeamMemberAdd,
    TeamMemberRemove,
    TeamMembersResponse,
    TeamUpdate,
    TeamSettingsResponse,
    TeamSettingsUpdate,
    TeamCreateWithSettings,
)
from app.crud import teams as crud
from app.api.dependencies import get_current_user
from app.crud import user as user_crud

router = APIRouter()

@router.post("/teams", response_model=TeamResponse)
def create_team_api(
    team: TeamCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    if not team.workspace_id:
        raise HTTPException(status_code=400, detail="workspace_id is required")
    created_team = crud.create_team(db=db, team=team)

    creator_and_provided_ids = []
    try:
        provided = team.user_ids or []
        seen = set()
        for uid in [str(user.user_id), *[str(u) for u in provided]]:
            if uid not in seen:
                creator_and_provided_ids.append(uid)
                seen.add(uid)
    except Exception:
        creator_and_provided_ids = [str(user.user_id)]
    if creator_and_provided_ids:
        crud.add_team_members(
            db=db,
            team_id=created_team.team_id,
            members=TeamMemberAdd(user_ids=creator_and_provided_ids),
        )
    return created_team

@router.post("/teams/settings", response_model=TeamResponse)
def create_team_with_settings_api(
    payload: TeamCreateWithSettings,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    if not payload.workspace_id:
        raise HTTPException(status_code=400, detail="workspace_id is required")
    return crud.create_team_with_settings(db=db, payload=payload)

@router.post("/teams/{team_id}/members", response_model=TeamResponse)
def add_team_members_api(
    team_id: str,
    members: TeamMemberAdd,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return crud.add_team_members(db=db, team_id=team_id, members=members)

@router.delete("/teams/{team_id}/members", response_model=TeamResponse)
def remove_team_members_api(
    team_id: str,
    members: TeamMemberRemove,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return crud.remove_team_members(db=db, team_id=team_id, members=members)

@router.get("/teams", response_model=list[TeamResponse])
def list_teams_api(
    workspace_id: str = Query(..., description="Workspace ID to filter teams"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return crud.get_all_teams(db=db, member_id=user.user_id, workspace_id=workspace_id)

@router.get("/teams/{team_id}/members", response_model=TeamMembersResponse)
def get_team_members_api(
    team_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return crud.get_team_members(db=db, team_id=team_id)

@router.get("/teams/{team_id}", response_model=TeamResponse)
def get_team_details_api(
    team_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return crud.get_team_details(db=db, team_id=team_id)

@router.patch("/teams", response_model=TeamResponse)
def update_team_api(
    payload: TeamUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return crud.update_team(db=db, payload=payload)

@router.get("/teams/{team_id}/settings", response_model=TeamSettingsResponse)
def get_team_settings_api(
    team_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return crud.get_team_settings(db=db, team_id=team_id)

@router.patch("/teams/{team_id}/settings", response_model=TeamSettingsResponse)
def update_team_settings_api(
    team_id: str,
    payload: TeamSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    payload.team_id = team_id
    return crud.update_team_settings(db=db, payload=payload)
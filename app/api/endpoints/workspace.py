from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.crud import user as user_crud
from app.crud import workspace as crud_workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse, WorkspaceUpdate, WorkspaceMemberRoleUpdate, WorkspaceMemberRoleResponse, WorkspaceMemberDetailsResponse
from app.schemas.teams import TeamResponse
from app.crud import teams as crud_teams

router = APIRouter()


@router.post("/workspaces", response_model=WorkspaceResponse)
def create_workspace_endpoint(
    workspace: WorkspaceCreate,
    tenant_id: str = Query(..., description="Tenant ID to create workspace under"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...),
):
    """Create a workspace for a given tenant. Auth required."""
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return crud_workspace.create_workspace(
        db=db,
        workspace=workspace,
        tenant_id=tenant_id,
        created_by=user.user_id,
    )


@router.get("/workspaces/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace_endpoint(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...),
):
    """Get a workspace by ID. Auth required."""
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    ws = crud_workspace.get_workspace_by_id(db, workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return WorkspaceResponse(
        workspace_id=ws.workspace_id,
        name=ws.name,
        tenant_id=ws.tenant_id,
        created_by=ws.created_by,
        description=ws.description,
        created_at=int(ws.created_at.timestamp()) if ws.created_at else None,
    )


@router.get("/workspaces", response_model=List[TeamResponse])
def list_workspaces_endpoint(
    workspace_id: str = Query(..., description="Required workspace ID"),
    member_id: Optional[str] = Query(None, description="Filter to teams this member belongs to; defaults to current user"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...),
):
    """List only teams you belong to in the given workspace. Auth required."""
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    effective_member_id = member_id if member_id else user.user_id
    return crud_teams.get_all_teams(db=db, member_id=effective_member_id, workspace_id=workspace_id)


@router.post("/workspaces/{workspace_id}/members/role", response_model=WorkspaceMemberRoleResponse)
def update_member_role_endpoint(
    workspace_id: str,
    payload: WorkspaceMemberRoleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...),
):
    """Creator/Admin can update a member's role to Admin/Member."""
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    ws = crud_workspace.get_workspace_by_id(db, workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    from app.models.workspace import WorkspaceMember
    requester_membership = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user.user_id,
    ).first()
    if ws.created_by != user.user_id and (not requester_membership or requester_membership.role != "Admin"):
        raise HTTPException(status_code=403, detail="Not authorized to update roles")
    return crud_workspace.update_workspace_member_role(db, workspace_id, payload)


@router.get("/workspaces/{workspace_id}/members/roles", response_model=List[WorkspaceMemberDetailsResponse])
def list_member_roles_endpoint(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...),
):
    """List all workspace members with their user details (name, email) and roles. Auth required."""
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    ws = crud_workspace.get_workspace_by_id(db, workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    from app.models.workspace import WorkspaceMember
    requester_membership = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user.user_id,
    ).first()
    if ws.created_by != user.user_id and (not requester_membership or requester_membership.role != "Admin"):
        raise HTTPException(status_code=403, detail="Not authorized to view roles")
    return crud_workspace.list_workspace_member_details(db, workspace_id)


@router.get("/workspaces/{workspace_id}/members", response_model=List[WorkspaceMemberDetailsResponse])
def list_workspace_members(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...),
):
    """Return all workspace members from DB with their name, email, and role.

    Requires requester to be the creator or an Admin member of the workspace.
    """
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")

    ws = crud_workspace.get_workspace_by_id(db, workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")

    from app.models.workspace import WorkspaceMember
    requester_membership = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user.user_id,
    ).first()
    if ws.created_by != user.user_id and (not requester_membership or requester_membership.role != "Admin"):
        raise HTTPException(status_code=403, detail="Not authorized to view members")

    return crud_workspace.list_workspace_member_details(db, workspace_id)


@router.patch("/workspaces", response_model=WorkspaceResponse)
def update_workspace_endpoint(
    payload: WorkspaceUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...),
):
    """Update workspace name/description. Auth required."""
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    ws = crud_workspace.get_workspace_by_id(db, payload.workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    if ws.created_by != user.user_id and ws.tenant_id != user.tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this workspace")
    return crud_workspace.update_workspace(db, payload)



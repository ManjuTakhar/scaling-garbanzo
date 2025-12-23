from sqlalchemy.orm import Session
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse, WorkspaceUpdate, WorkspaceMemberRoleUpdate, WorkspaceMemberRoleResponse, WorkspaceMemberDetailsResponse
from typing import List, Optional

def create_workspace(db: Session, workspace: WorkspaceCreate, tenant_id: str, created_by: str) -> WorkspaceResponse:
    """Create a new workspace."""
    # Enforce one workspace per tenant: check if a workspace already exists for this tenant
    existing = db.query(Workspace).filter(Workspace.tenant_id == tenant_id).first()
    if existing is not None:
        raise ValueError("A workspace already exists for this tenant. Only one workspace per tenant is allowed.")
    db_workspace = Workspace(
        name=workspace.name,
        tenant_id=tenant_id,
        created_by=created_by,
        description=workspace.description,
        settings=workspace.settings
    )
    
    db.add(db_workspace)
    db.commit()
    db.refresh(db_workspace)
    
    # Ensure creator is also a member of the workspace with Admin role
    try:
        from app.models.workspace import WorkspaceMember
        from app.models.user import User
        # Only add membership if the creator exists and not already a member
        creator = db.query(User).filter(User.user_id == created_by).first()
        if creator is not None:
            existing_membership = db.query(WorkspaceMember).filter(
                WorkspaceMember.workspace_id == db_workspace.workspace_id,
                WorkspaceMember.user_id == created_by,
            ).first()
            if existing_membership is None:
                db.add(WorkspaceMember(
                    workspace_id=db_workspace.workspace_id,
                    user_id=created_by,
                    role="Admin",
                ))
                # Also set the creator's active workspace to the newly created one
                creator.workspace_id = db_workspace.workspace_id
                db.commit()
    except Exception:
        # Non-fatal: if membership insert fails in testing (e.g. missing user), continue
        db.rollback()
    
    return WorkspaceResponse(
        workspace_id=db_workspace.workspace_id,
        name=db_workspace.name,
        tenant_id=db_workspace.tenant_id,
        created_by=db_workspace.created_by,
        description=db_workspace.description,
        created_at=int(db_workspace.created_at.timestamp()) if db_workspace.created_at else None
    )

def get_workspace_by_id(db: Session, workspace_id: str) -> Optional[Workspace]:
    """Get workspace by ID."""
    return db.query(Workspace).filter(Workspace.workspace_id == workspace_id).first()

def get_workspaces_by_tenant(db: Session, tenant_id: str) -> List[Workspace]:
    """Get all workspaces for a tenant."""
    return db.query(Workspace).filter(Workspace.tenant_id == tenant_id).all()

def get_workspaces_by_user(db: Session, user_id: str) -> List[Workspace]:
    """Get all workspaces created by a user."""
    return db.query(Workspace).filter(Workspace.created_by == user_id).all()

def get_workspace_members(db: Session, workspace_id: str, user_id: str) -> List[Workspace]:
    """Get workspace members for a specific workspace. Only returns workspace if user is a member."""
    from app.models.workspace import WorkspaceMember
    
    # Join workspace with workspace_members to check if user is a member
    workspace = db.query(Workspace).join(WorkspaceMember).filter(
        Workspace.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id
    ).first()
    
    return [workspace] if workspace else []


def update_workspace(db: Session, payload: WorkspaceUpdate) -> WorkspaceResponse:
    """Update a workspace's name and/or description."""
    ws = db.query(Workspace).filter(Workspace.workspace_id == payload.workspace_id).first()
    if not ws:
        raise ValueError("Workspace not found")

    if payload.name is not None:
        ws.name = payload.name
    if payload.description is not None:
        ws.description = payload.description

    db.commit()
    db.refresh(ws)

    return WorkspaceResponse(
        workspace_id=ws.workspace_id,
        name=ws.name,
        tenant_id=ws.tenant_id,
        created_by=ws.created_by,
        description=ws.description,
        created_at=int(ws.created_at.timestamp()) if ws.created_at else None,
    )


def update_workspace_member_role(db: Session, workspace_id: str, payload: WorkspaceMemberRoleUpdate) -> WorkspaceMemberRoleResponse:
    """Update a member's role in a workspace."""
    from app.models.workspace import WorkspaceMember
    membership = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == payload.user_id,
    ).first()
    if not membership:
        raise ValueError("Workspace membership not found")

    membership.role = payload.role
    db.commit()
    db.refresh(membership)
    return WorkspaceMemberRoleResponse(user_id=membership.user_id, role=membership.role)


def list_workspace_member_roles(db: Session, workspace_id: str) -> List[WorkspaceMemberRoleResponse]:
    from app.models.workspace import WorkspaceMember
    memberships = db.query(WorkspaceMember).filter(WorkspaceMember.workspace_id == workspace_id).all()
    return [WorkspaceMemberRoleResponse(user_id=m.user_id, role=m.role) for m in memberships]


def list_workspace_member_details(db: Session, workspace_id: str) -> List[WorkspaceMemberDetailsResponse]:
    """List all workspace members with their user details (name, email) and roles."""
    from app.models.workspace import WorkspaceMember
    from app.models.user import User
    
    # Join WorkspaceMember with User to get user details
    memberships = db.query(WorkspaceMember, User).join(
        User, WorkspaceMember.user_id == User.user_id
    ).filter(WorkspaceMember.workspace_id == workspace_id).all()
    
    return [
        WorkspaceMemberDetailsResponse(
            user_id=membership.user_id,
            name=user.name,
            email=user.email,
            role=membership.role
        )
        for membership, user in memberships
    ]


def get_workspace_member_by_user_id(db: Session, workspace_id: str, user_id: str):
    """Return membership row for a user in a workspace, or None if not a member."""
    from app.models.workspace import WorkspaceMember
    return db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id,
    ).first()
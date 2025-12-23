from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException
from app.models.workspace_invitation import WorkspaceInvitation
from app.models.workspace import Workspace, WorkspaceMember
from app.models.user import User
from app.schemas.workspace_invitation import WorkspaceInvitationCreate, WorkspaceInvitationResponse, WorkspaceInvitationAccept, MagicLinkResponse
from app.schemas.user import UserCreate
from app.crud.user import create_user
from app.utils.utils import generate_custom_id
from datetime import datetime, timedelta, timezone
import secrets
import hashlib
from typing import List, Optional


def generate_magic_token() -> str:
    """Generate a secure magic token for invitation links"""
    return secrets.token_urlsafe(32)


def create_workspace_invitation_with_token(
    db: Session, 
    workspace_id: str, 
    invitation_data: WorkspaceInvitationCreate, 
    invited_by: str
) -> dict:
    """Create a new workspace invitation and return both invitation and magic token"""
    
    # Check if workspace exists
    workspace = db.query(Workspace).filter(Workspace.workspace_id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Check if user is already a member
    existing_member = db.query(WorkspaceMember).filter(
        and_(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id.in_(
                db.query(User.user_id).filter(User.email == invitation_data.email)
            )
        )
    ).first()
    
    if existing_member:
        raise HTTPException(status_code=400, detail="User is already a member of this workspace")
    
    # Allow multiple invitations - removed duplicate check
    # Generate magic token and expiration
    magic_token = generate_magic_token()
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)  # 7 days expiry
    
    # Create invitation with timestamp to ensure uniqueness
    timestamp = int(datetime.now(timezone.utc).timestamp())
    invitation_id = f"INV-{generate_custom_id(invitation_data.email)}-{timestamp}"
    
    db_invitation = WorkspaceInvitation(
        invitation_id=invitation_id,
        workspace_id=workspace_id,
        email=invitation_data.email,
        invited_by=invited_by if invited_by != "system" else None,
        role=invitation_data.role,
        magic_token=magic_token,
        expires_at=expires_at
    )
    
    db.add(db_invitation)
    db.commit()
    db.refresh(db_invitation)
    
    invitation_response = WorkspaceInvitationResponse(
        invitation_id=db_invitation.invitation_id,
        workspace_id=db_invitation.workspace_id,
        email=db_invitation.email,
        invited_by=db_invitation.invited_by,
        role=db_invitation.role,
        is_accepted=db_invitation.is_accepted,
        expires_at=int(db_invitation.expires_at.timestamp()),
        created_at=int(db_invitation.created_at.timestamp()),
        accepted_at=int(db_invitation.accepted_at.timestamp()) if db_invitation.accepted_at else None
    )
    
    return {
        "invitation": invitation_response,
        "magic_token": magic_token
    }


def create_workspace_invitation(
    db: Session, 
    workspace_id: str, 
    invitation_data: WorkspaceInvitationCreate, 
    invited_by: str
) -> WorkspaceInvitationResponse:
    """Create a new workspace invitation"""
    
    # Check if workspace exists
    workspace = db.query(Workspace).filter(Workspace.workspace_id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Check if user is already a member
    existing_member = db.query(WorkspaceMember).filter(
        and_(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id.in_(
                db.query(User.user_id).filter(User.email == invitation_data.email)
            )
        )
    ).first()
    
    if existing_member:
        raise HTTPException(status_code=400, detail="User is already a member of this workspace")
    
    # Check if there's already a pending invitation
    existing_invitation = db.query(WorkspaceInvitation).filter(
        and_(
            WorkspaceInvitation.workspace_id == workspace_id,
            WorkspaceInvitation.email == invitation_data.email,
            WorkspaceInvitation.is_accepted == False,
            WorkspaceInvitation.expires_at > datetime.now(timezone.utc)
        )
    ).first()
    
    if existing_invitation:
        raise HTTPException(status_code=400, detail="Invitation already sent to this email")
    
    # Generate magic token and expiration
    magic_token = generate_magic_token()
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)  # 7 days expiry
    
    # Create invitation
    invitation_id = f"INV-{generate_custom_id(invitation_data.email)}"
    
    db_invitation = WorkspaceInvitation(
        invitation_id=invitation_id,
        workspace_id=workspace_id,
        email=invitation_data.email,
        invited_by=invited_by if invited_by != "system" else None,
        role=invitation_data.role,
        magic_token=magic_token,
        expires_at=expires_at
    )
    
    db.add(db_invitation)
    db.commit()
    db.refresh(db_invitation)
    
    return WorkspaceInvitationResponse(
        invitation_id=db_invitation.invitation_id,
        workspace_id=db_invitation.workspace_id,
        email=db_invitation.email,
        invited_by=db_invitation.invited_by,
        role=db_invitation.role,
        is_accepted=db_invitation.is_accepted,
        expires_at=int(db_invitation.expires_at.timestamp()),
        created_at=int(db_invitation.created_at.timestamp()),
        accepted_at=int(db_invitation.accepted_at.timestamp()) if db_invitation.accepted_at else None
    )


def validate_magic_link(db: Session, magic_token: str) -> MagicLinkResponse:
    """Validate a magic link token and return invitation details"""
    
    invitation = db.query(WorkspaceInvitation).filter(
        WorkspaceInvitation.magic_token == magic_token
    ).first()
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invalid invitation link")
    
    if invitation.is_accepted:
        raise HTTPException(status_code=400, detail="Invitation has already been accepted")
    
    if invitation.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invitation link has expired")
    
    # Get workspace details
    workspace = db.query(Workspace).filter(Workspace.workspace_id == invitation.workspace_id).first()
    
    return MagicLinkResponse(
        invitation_id=invitation.invitation_id,
        workspace_id=invitation.workspace_id,
        workspace_name=workspace.name if workspace else "Unknown Workspace",
        email=invitation.email,
        role=invitation.role,
        expires_at=int(invitation.expires_at.timestamp()),
        is_valid=True
    )


def accept_workspace_invitation(
    db: Session, 
    invitation_data: WorkspaceInvitationAccept
) -> dict:
    """Accept a workspace invitation and create user if needed"""
    
    # Validate magic link
    invitation = db.query(WorkspaceInvitation).filter(
        WorkspaceInvitation.magic_token == invitation_data.magic_token
    ).first()
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invalid invitation link")
    
    if invitation.is_accepted:
        raise HTTPException(status_code=400, detail="Invitation has already been accepted")
    
    if invitation.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invitation link has expired")
    
    # Check if user exists
    user = db.query(User).filter(User.email == invitation.email).first()
    
    if not user:
        # Create new user with the invited workspace_id set
        user_data = UserCreate(
            email=invitation.email,
            name=invitation_data.name or invitation.email.split('@')[0],  # Use email prefix as default name
            picture=invitation_data.picture,
            role="Engineer",  # Default role
            tenant_id=invitation.workspace.tenant_id,  # Use workspace's tenant
            workspace_id=invitation.workspace_id  # Set the invited workspace as active
        )
        user = create_user(db, user_data)
    else:
        # Update existing user's tenant_id to match the workspace's tenant for consistency
        if user.tenant_id != invitation.workspace.tenant_id:
            user.tenant_id = invitation.workspace.tenant_id
        
        # Set the user's active workspace_id to the invited workspace
        user.workspace_id = invitation.workspace_id
    
    # Check if user is already a member of this workspace
    existing_member = db.query(WorkspaceMember).filter(
        and_(
            WorkspaceMember.workspace_id == invitation.workspace_id,
            WorkspaceMember.user_id == user.user_id
        )
    ).first()
    
    if not existing_member:
        # Add user to workspace
        workspace_member = WorkspaceMember(
            workspace_id=invitation.workspace_id,
            user_id=user.user_id,
            role=invitation.role
        )
        db.add(workspace_member)

    # Mark invitation as accepted
    invitation.is_accepted = True
    invitation.accepted_at = datetime.now(timezone.utc)
    
    db.commit()
    
    return {
        "message": "Successfully joined workspace",
        "workspace_id": invitation.workspace_id,
        "workspace_name": invitation.workspace.name,
        "user_id": user.user_id,
        "role": invitation.role
    }


def list_workspace_invitations(
    db: Session, 
    workspace_id: str, 
    user_id: str
) -> List[WorkspaceInvitationResponse]:
    """List all pending invitations for a workspace (only for workspace admins/creator)"""
    
    # Check if user has permission to view invitations
    workspace = db.query(Workspace).filter(Workspace.workspace_id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Check if user is creator or admin
    is_creator = (workspace.created_by == user_id)
    member = db.query(WorkspaceMember).filter(
        and_(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id
        )
    ).first()
    is_admin = (member and member.role == "Admin") if member else False
    
    if not (is_creator or is_admin):
        raise HTTPException(status_code=403, detail="Not authorized to view workspace invitations")
    
    # Get pending invitations
    invitations = db.query(WorkspaceInvitation).filter(
        and_(
            WorkspaceInvitation.workspace_id == workspace_id,
            WorkspaceInvitation.is_accepted == False,
            WorkspaceInvitation.expires_at > datetime.now(timezone.utc)
        )
    ).all()
    
    return [
        WorkspaceInvitationResponse(
            invitation_id=inv.invitation_id,
            workspace_id=inv.workspace_id,
            email=inv.email,
            invited_by=inv.invited_by,
            role=inv.role,
            is_accepted=inv.is_accepted,
            expires_at=int(inv.expires_at.timestamp()),
            created_at=int(inv.created_at.timestamp()),
            accepted_at=int(inv.accepted_at.timestamp()) if inv.accepted_at else None
        )
        for inv in invitations
    ]


def cancel_workspace_invitation(
    db: Session, 
    invitation_id: str, 
    user_id: str
) -> dict:
    """Cancel a workspace invitation (only for workspace admins/creator)"""
    
    invitation = db.query(WorkspaceInvitation).filter(
        WorkspaceInvitation.invitation_id == invitation_id
    ).first()
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    # Check if user has permission to cancel invitation
    workspace = db.query(Workspace).filter(Workspace.workspace_id == invitation.workspace_id).first()
    is_creator = (workspace.created_by == user_id)
    member = db.query(WorkspaceMember).filter(
        and_(
            WorkspaceMember.workspace_id == invitation.workspace_id,
            WorkspaceMember.user_id == user_id
        )
    ).first()
    is_admin = (member and member.role == "Admin") if member else False
    
    if not (is_creator or is_admin):
        raise HTTPException(status_code=403, detail="Not authorized to cancel this invitation")
    
    db.delete(invitation)
    db.commit()
    
    return {"message": "Invitation cancelled successfully"}

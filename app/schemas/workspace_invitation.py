from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class WorkspaceInvitationCreate(BaseModel):
    """Schema for creating a workspace invitation"""
    email: EmailStr
    role: str = "Member"  # "Admin" | "Member"


class WorkspaceInvitationResponse(BaseModel):
    """Response model for workspace invitation details"""
    invitation_id: str
    workspace_id: str
    email: str
    invited_by: Optional[str] = None
    role: str
    is_accepted: bool
    expires_at: int  # Timestamp
    created_at: int  # Timestamp
    accepted_at: Optional[int] = None  # Timestamp

    class Config:
        from_attributes = True


class WorkspaceInvitationAccept(BaseModel):
    """Schema for accepting a workspace invitation"""
    magic_token: str
    name: Optional[str] = None  # User's name if they don't exist yet
    picture: Optional[str] = None  # User's picture if they don't exist yet


class WorkspaceInvitationListResponse(BaseModel):
    """Response model for listing workspace invitations"""
    workspace_id: str
    pending_invitations: List[WorkspaceInvitationResponse]
    total_count: int


class MagicLinkResponse(BaseModel):
    """Response model for magic link validation"""
    invitation_id: str
    workspace_id: str
    workspace_name: str
    email: str
    role: str
    expires_at: int
    is_valid: bool


class WorkspaceInvitationLinkResponse(BaseModel):
    """Response model for workspace invitation link generation"""
    invitation_id: str
    workspace_id: str
    email: str
    role: str
    magic_link: str
    expires_at: int
    created_at: int

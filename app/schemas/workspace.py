from pydantic import BaseModel
from typing import Optional

class WorkspaceBase(BaseModel):
    name: str
    description: Optional[str] = None
    settings: Optional[str] = None  # JSON string for workspace settings

class WorkspaceCreate(WorkspaceBase):
    """Schema for creating a new workspace"""
    pass

class WorkspaceResponse(BaseModel):
    """Response model for workspace details"""
    workspace_id: str
    name: str
    tenant_id: str
    created_by: str
    description: Optional[str] = None
    created_at: Optional[int] = None  # Timestamp

    class Config:
        from_attributes = True


class WorkspaceUpdate(BaseModel):
    """Schema for updating a workspace's basic fields"""
    workspace_id: str
    name: Optional[str] = None
    description: Optional[str] = None


class WorkspaceMemberRoleUpdate(BaseModel):
    """Payload to update a member's role within a workspace."""
    user_id: str
    role: str  # "Admin" | "Member"


class WorkspaceMemberRoleResponse(BaseModel):
    user_id: str
    role: str


class WorkspaceMemberDetailsResponse(BaseModel):
    """Response model for workspace member details including user info and role"""
    user_id: str
    name: str
    email: str
    role: str
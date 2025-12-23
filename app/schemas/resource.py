from pydantic import BaseModel
from typing import Optional
from app.dto.dtos import UserDTO

class ResourceBase(BaseModel):
    title: str
    url: str
    type: str


class ResourceCreate(ResourceBase):
    """Schema for creating a resource"""
    created_by: str
    pinned: Optional[bool] = False

class ProjectResourceResponse(ResourceBase):
    resource_id: str
    project_id: str
    created_at: int
    last_updated: int
    created_by: UserDTO
    pinned: bool

class InitiativeResourceResponse(ResourceBase):
    resource_id: str
    initiative_id: str
    created_at: int
    last_updated: int
    created_by: UserDTO
    pinned: bool

class ResourceUpdate(BaseModel):
    """Schema for updating a resource"""
    title: Optional[str] = None
    url: Optional[str] = None
    type: Optional[str] = None
    created_by: Optional[str] = None 
    pinned: Optional[bool] = None
from pydantic import BaseModel
from typing import List, Optional, Any
from app.schemas.user import UserResponse
from app.dto.dtos import UserDTO

class TeamBase(BaseModel):
    name: Optional[str] = None
    user_ids: Optional[List[str]] = None 

class Team(TeamBase):
    team_id: str
    created_at: Optional[int] = None  # Timestamp
    members: Optional[List[UserResponse]] = None  # Include members in the response

    class Config:
        from_attributes = True

class TeamCreate(TeamBase):
    """Schema for creating a new team, with optional user IDs"""
    name: Optional[str] = None
    description: Optional[str] = None
    workspace_id: str  # Required
    user_ids: Optional[List[str]] = None 


class TeamUpdate(BaseModel):
    """Schema for updating team basic fields"""
    team_id: str
    name: Optional[str] = None
    description: Optional[str] = None

class TeamResponse(BaseModel):
    """Response model for returning team details"""
    team_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    workspace_id: Optional[str] = None  # Include workspace_id in response
    created_at: Optional[int] = None  # Timestamp
    members: Optional[List[UserDTO]] = None  # Include members in the response
    settings: Optional[str] = None
    class Config:
        from_attributes = True  # ✅ Fixes ORM mode issue in Pydantic V2


class TeamMemberAdd(BaseModel):
    """Schema for adding users to a team"""
    user_ids: List[str]

class TeamMemberRemove(BaseModel):
    """Schema for removing users from a team"""
    user_ids: List[str]

class TeamMemberResponse(BaseModel):
    """Schema for returning a team member"""
    user_id: str

class TeamMembersResponse(BaseModel):
    """Schema for returning all members of a team"""
    team_id: str
    members: Optional[List[UserResponse]] = None  # ✅ Return full user details, not just user_id


class TeamSettingsResponse(BaseModel):
    team_id: str
    general_settings: dict
    issue_settings: dict
    cycle_configuration: dict
    members: List[dict]


class TeamSettingsUpdate(BaseModel):
    team_id: Optional[str] = None
    general_settings: Optional[dict] = None
    issue_settings: Optional[dict] = None
    cycle_configuration: Optional[dict] = None
    user_ids: Optional[List[str]] = None
    updated_by: Optional[str] = None


class TeamCreateWithSettings(TeamCreate):
    general_settings: Optional[dict] = None
    issue_settings: Optional[dict] = None
    cycle_configuration: Optional[dict] = None
    user_ids: Optional[List[str]] = None

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from app.schemas.user import UserResponse, User  # Import UserResponse
from app.schemas.teams import TeamResponse, Team  # Import TeamResponse
from app.dto.dtos import UserDTO, TeamDTO, ChannelDTO, InitiativeUpdateDTO
from app.schemas.health import InitiativeHealthSummary

class StatusEnum(str, Enum):
    On_Track = "On Track"
    At_Risk = "At Risk"
    Blocked = "Blocked"
    Completed = "Completed"

class InitiativeBase(BaseModel):
    title: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=255)
    description: Optional[Dict[str, Any]] = None  # Accept any valid JSON
    status: Optional[str] = None
    progress: Optional[int] = None
    start_date: Optional[int] = None  # Change to timestamp
    end_date: Optional[int] = None  # Change to timestamp
    priority: Optional[str] = None

class InitiativeCreate(InitiativeBase):
    workspace_id: str  # Use workspace_id instead of workspace_id
    owner_id: Optional[str] = None  # Change to UserResponse
    teams: Optional[List[str]] = []  # List of teams associated with the initiative
    channels: Optional[List[str]] = []  # List of channels associated with the initiative

class InitiativeUpdate(InitiativeBase):
    workspace_id: Optional[str] = None  # Use workspace_id instead of workspace_id
    owner_id: Optional[str] = None
    teams: Optional[List[str]] = []
    channels: Optional[List[str]] = []


class InitiativeResponse(BaseModel):
    initiative_id: str
    title: str
    short_description: Optional[str] = Field(None, max_length=255)
    description: Optional[Dict[str, Any]] = None
    owner: Optional[UserDTO] = None  # Change to UserResponse
    status: str
    progress: int
    start_date: Optional[int] = None  # Change to timestamp
    end_date: Optional[int] = None  # Change to timestamp
    workspace_id: str  # Correctly use workspace_id
    created_at: Optional[int] = None  # Timestamp
    last_updated: Optional[int] = None
    teams: Optional[List[TeamDTO]] = []  # List of teams associated with the initiative
    channels: Optional[List[ChannelDTO]] = []  # List of channels associated with the initiative
    priority: Optional[str] = None
    contributors: Optional[List[UserDTO]] = []  # List of contributors associated with the initiative
    latest_update: Optional[InitiativeUpdateDTO] = None
    health: Optional[InitiativeHealthSummary] = None
    class Config:
        orm_mode = True

class Initiative(InitiativeBase):
    initiative_id: str
    created_at: int  # Change to timestamp
    last_updated: int  # Change to timestamp

    class Config:
        orm_mode = True

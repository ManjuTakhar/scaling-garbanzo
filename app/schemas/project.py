from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum
from app.schemas.user import User, UserResponse
from uuid import UUID
from app.schemas.teams import TeamResponse, Team
from app.schemas.health import ProjectHealthSummary
from app.dto.dtos import UserDTO, TeamDTO, ChannelDTO, ProjectUpdateDTO

class StatusEnum(str, Enum):
    On_Track = "On Track"
    At_Risk = "At Risk"
    Blocked = "Blocked"
    Completed = "Completed"

class StageEnum(str, Enum):
    Planning = "Planning"
    Execution = "Execution"
    Complete = "Complete"

class ProjectBase(BaseModel):
    title: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=255)
    description: Optional[Dict[str, Any]] = None  # Simplified to accept any valid JSON
    initiative_id: Optional[str] = None
    status: Optional[str] = None    
    stage: Optional[str] = None
    progress: Optional[int] = None
    start_date: Optional[int] = None
    end_date: Optional[int] = None
    workspace_id: Optional[str] = None
    priority: Optional[str] = None
    

class ProjectCreate(ProjectBase):
    teams: Optional[List[str]] = None
    channels: Optional[List[str]] = None
    dri_id: Optional[str] = None

class Project(ProjectBase):
    project_id: str
    created_at: int
    last_updated: int

    class Config:
        orm_mode = True

class ProjectUpdate(ProjectBase):
    dri_id: Optional[str] = None
    teams: Optional[List[str]] = None
    channels: Optional[List[str]] = None

class ProjectResponse(Project):
    dri: Optional[UserDTO] = None   
    teams: Optional[List[TeamDTO]] = None
    channels: Optional[List[ChannelDTO]] = None
    contributors: Optional[List[UserDTO]] = None
    latest_update: Optional[ProjectUpdateDTO] = None
    health: Optional[ProjectHealthSummary] = None
    class Config:
        orm_mode = True

class MilestoneBase(BaseModel):
    title: str
    target_date: Optional[int] = None
    status: str

class MilestoneCreate(MilestoneBase):
    dri: str
    pass

class Milestone(MilestoneBase):
    milestone_id: str
    project_id: str
    created_at: Optional[int] = None
    last_updated: Optional[int] = None

    class Config:
        orm_mode = True

class MilestoneResponse(Milestone):
    dri: Optional[UserDTO] = None
    class Config:
        orm_mode = True

class MilestoneUpdate(BaseModel):
    title: Optional[str] = None
    dri: Optional[str] = None
    target_date: Optional[datetime] = None
    status: Optional[str] = None

class ProjectDetail(Project):
    milestones: List[Milestone]
    contributors: List[User]
    teams: List[str]


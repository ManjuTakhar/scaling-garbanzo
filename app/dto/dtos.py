from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class UserDTO(BaseModel):
    user_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    picture: Optional[str] = None
    tenant_id: Optional[str] = None

class TeamDTO(BaseModel):
    team_id: str
    name: str

class LabelDTO(BaseModel):
    id: str
    name: str
    color: Optional[str] = None
    description: Optional[str] = None

class IssueDTO(BaseModel):
    id: Optional[str] = None
    display_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[Dict[str, Any]] = None
    acceptance_criteria: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    issue_type: Optional[str] = None
    assignee: Optional[UserDTO] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    start_date: Optional[int] = None
    due_date: Optional[int] = None
    story_points: Optional[int] = None
    cycle_id: Optional[str] = None
    epic_id: Optional[str] = None
    created_by: Optional[UserDTO] = None
    team: Optional[TeamDTO] = None
    labels: Optional[List[LabelDTO]] = None
    is_archived: Optional[bool] = None

class EpicDTO(BaseModel):
    id: Optional[str] = None
    display_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    start_date: Optional[int] = None
    due_date: Optional[int] = None
    cycle_id: Optional[str] = None
    team_id: Optional[str] = None
    created_by: Optional[UserDTO] = None
    updated_by: Optional[UserDTO] = None

class CycleDTO(BaseModel):
    id: Optional[str] = None
    display_id: Optional[str] = None
    name: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[int] = None
    due_date: Optional[int] = None
    completed_at: Optional[int] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    created_by: Optional[UserDTO] = None
    team_id: Optional[str] = None
    description: Optional[str] = None

class CycleUpdateDTO(BaseModel):
    id: Optional[str] = None
    cycle_id: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    created_by: Optional[UserDTO] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    updated_by: Optional[UserDTO] = None

class ChannelDTO(BaseModel):
    channel_id: str
    name: str

class ProjectDTO(BaseModel):
    project_id: str
    title: str
    short_description: Optional[str] = Field(None, max_length=255)
    description: Optional[Dict[str, Any]] = None  # Simplified to accept any valid JSON
    initiative_id: Optional[str] = None
    status: Optional[str] = None    
    stage: Optional[str] = None
    progress: Optional[int] = None
    start_date: Optional[int] = None
    end_date: Optional[int] = None
    tenant_id: Optional[str] = None
    created_at: Optional[int] = None
    last_updated: Optional[int] = None
    dri: Optional[UserDTO] = None

class InitiativeDTO(BaseModel):
    initiative_id: str
    title: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=255)
    description: Optional[Dict[str, Any]] = None  # Simplified to accept any valid JSON
    status: Optional[str] = None
    progress: Optional[int] = None
    start_date: Optional[int] = None
    end_date: Optional[int] = None
    tenant_id: Optional[str] = None
    created_at: Optional[int] = None
    last_updated: Optional[int] = None
    owner: Optional[UserDTO] = None

class ProjectUpdateDTO(BaseModel):
    update_id: str
    created_at: int
    content: Dict[str, Any]
    current_status: Optional[str] = None

class InitiativeUpdateDTO(BaseModel):
    update_id: str
    created_at: int
    content: Dict[str, Any]
    current_status: Optional[str] = None

class DependencyInitiativeDTO(BaseModel):
    initiative_id: str
    title: str
    status: str
    owner: Optional[UserDTO] = None

class DependencyProjectDTO(BaseModel):
    project_id: str
    title: str
    status: str
    dri: Optional[UserDTO] = None

class InitiativeDependencyDTO(BaseModel):
    dependency_id: str
    type: str
    initiative: DependencyInitiativeDTO
    status: str
    created_at: int
    last_updated: int
    created_by: UserDTO
    description: Optional[str] = None

class ProjectDependencyDTO(BaseModel):
    dependency_id: str
    type: str
    project: DependencyProjectDTO
    status: str
    created_at: int
    last_updated: int
    created_by: UserDTO
    description: Optional[str] = None
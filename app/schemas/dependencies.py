from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.dto.dtos import UserDTO, DependencyInitiativeDTO, DependencyProjectDTO
from app.models.dependencies import DependencyType

class InitiativeDependency(BaseModel):
    dependency_id: str
    type: DependencyType
    created_by: UserDTO
    description: Optional[str] = None
    created_at: int
    last_updated: int

class InitiativeDependencyCreate(BaseModel):
    type: DependencyType
    initiative_id: str
    description: Optional[str] = None
    created_by: str
    status: str = "active"

class InitiativeDependencyResponse(BaseModel):
    dependency_id: str
    type: DependencyType
    initiative: DependencyInitiativeDTO
    status: str
    created_at: int
    last_updated: int
    created_by: UserDTO
    updated_by: Optional[UserDTO] = None
    description: Optional[str] = None

class ProjectDependencyCreate(BaseModel):
    project_id: str
    description: Optional[str] = None
    created_by: str
    status: Optional[str] = None
    type: DependencyType

class ProjectDependencyResponse(BaseModel):
    dependency_id: str
    type: DependencyType
    project: DependencyProjectDTO
    status: str
    created_at: int
    last_updated: int
    created_by: UserDTO
    updated_by: Optional[UserDTO] = None
    description: Optional[str] = None

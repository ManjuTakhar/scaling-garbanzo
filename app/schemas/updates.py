from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional, List
from app.dto.dtos import UserDTO

class UpdateBase(BaseModel):
    content: Dict[str, Any]
    current_status: Optional[str] = None

class UpdateCreate(UpdateBase):
    created_by: str
    tenant_id: Optional[str] = None
    channels_to_post: Optional[List[str]] = None

class Update(UpdateBase):
    update_id: str
    created_at: int

    class Config:
        orm_mode = True

class ProjectUpdate(Update):
    project_id: str

class InitiativeUpdate(Update):
    initiative_id: str

class ProjectUpdateResponse(ProjectUpdate):
    project_id: str
    created_by: UserDTO

class InitiativeUpdateResponse(InitiativeUpdate):
    initiative_id: str
    created_by: UserDTO

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List
from app.dto.dtos import UserDTO

class ProjectReactionBase(BaseModel):
    reaction_type: str
    reacted_by: str

class ProjectReactionCreate(ProjectReactionBase):
    pass

class ProjectReaction(ProjectReactionBase):
    id: str
    created_at: int
    
    model_config = ConfigDict(from_attributes=True)

class ProjectCommentBase(BaseModel):
    content: str
    created_by: str

class ProjectCommentCreate(ProjectCommentBase):
    pass

# Simple response model without nested relationships
class ProjectCommentResponse(BaseModel):
    content: str
    comment_id: str
    created_at: int
    update_id: str
    created_by: UserDTO
    
    model_config = ConfigDict(from_attributes=True)

class ProjectReactionResponse(BaseModel):
    reaction_type: str
    reacted_by: UserDTO
    reaction_id: str
    created_at: int
    update_id: str
    model_config = ConfigDict(from_attributes=True)

# Full model combining comments and reactions for GET requests
class ProjectInteractionResponse(BaseModel):
    comments: List[ProjectCommentResponse]
    reactions: List[ProjectReactionResponse]

ProjectCommentResponse.model_rebuild()
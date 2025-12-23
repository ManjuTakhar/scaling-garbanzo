from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from app.dto.dtos import UserDTO
class InitiativeReactionBase(BaseModel):
    reaction_type: str
    reacted_by: str

class InitiativeReactionCreate(InitiativeReactionBase):
    pass

class InitiativeReaction(InitiativeReactionBase):
    reaction_id: str
    created_at: int
    
    model_config = ConfigDict(from_attributes=True)

class InitiativeCommentBase(BaseModel):
    content: str
    created_by: str

class InitiativeCommentCreate(InitiativeCommentBase):
    pass

# Add this new response model
class InitiativeCommentResponse(BaseModel):
    content: str
    comment_id: str
    created_at: int
    update_id: str
    created_by: UserDTO
    
    model_config = ConfigDict(from_attributes=True)

class InitiativeReactionResponse(BaseModel):
    reaction_id: str
    reaction_type: str
    reacted_by: UserDTO
    created_at: int
    update_id: str

    model_config = ConfigDict(from_attributes=True)

class InitiativeInteractionResponse(BaseModel):
    comments: List[InitiativeCommentResponse]
    reactions: List[InitiativeReactionResponse]

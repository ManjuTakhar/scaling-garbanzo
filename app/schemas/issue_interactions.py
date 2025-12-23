from pydantic import BaseModel
from typing import List, Optional
from app.dto.dtos import UserDTO


class CommentReactionCreate(BaseModel):
    reaction_type: str
    created_by: str


class IssueCommentCreate(BaseModel):
    content: str
    created_by: str
    parent_comment_id: Optional[str] = None


class CommentReactionSummary(BaseModel):
    reaction_type: str
    count: int


class IssueCommentResponse(BaseModel):
    id: str
    content: str
    created_at: int
    issue_id: str
    created_by: UserDTO
    reactions: List[CommentReactionSummary] = []
    replies_count: Optional[int] = None
    last_reply_at: Optional[int] = None


class IssueInteractionResponse(BaseModel):
    comments: List[IssueCommentResponse]



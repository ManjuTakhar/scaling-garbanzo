from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
from sqlalchemy.dialects.postgresql import TIMESTAMP
from app.core.utils import generate_alphanumeric_id

class IssueComment(Base):
    __tablename__ = "issue_comments"
    
    id = Column(String, primary_key=True, default=lambda: f"comm-{generate_alphanumeric_id()}")
    parent_comment_id = Column(String, ForeignKey("issue_comments.id"), nullable=True)
    content = Column(String, nullable=False)
    created_by = Column(String, ForeignKey("users.user_id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True)
    issue_id = Column(String, ForeignKey("issues.id"))

    created_by_user = relationship("User", foreign_keys=[created_by])
    replies = relationship("IssueComment", backref="parent_comment", remote_side=[id])

class CommentReaction(Base):
    __tablename__ = "comment_reactions"
    
    id = Column(String, primary_key=True, default=lambda: f"rxn-{generate_alphanumeric_id()}")
    comment_id = Column(String, ForeignKey("issue_comments.id"), nullable=False)
    created_by = Column(String, ForeignKey("users.user_id"), nullable=False)
    reaction_type = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True)

    created_by_user = relationship("User", foreign_keys=[created_by])


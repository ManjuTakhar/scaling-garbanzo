from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
from sqlalchemy.dialects.postgresql import TIMESTAMP

class ProjectComment(Base):
    __tablename__ = "project_comments"
    
    comment_id = Column(String, primary_key=True)
    content = Column(String, nullable=False)
    created_by = Column(String, ForeignKey("users.user_id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    update_id = Column(String, ForeignKey("project_updates.update_id"))

    created_by_user = relationship("User", foreign_keys=[created_by])

class ProjectReaction(Base):
    __tablename__ = "project_reactions"
    
    reaction_id = Column(String, primary_key=True)
    update_id = Column(String, ForeignKey("project_updates.update_id"))
    reacted_by = Column(String, ForeignKey("users.user_id"), nullable=False)
    reaction_type = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    reacted_by_user = relationship("User", foreign_keys=[reacted_by])

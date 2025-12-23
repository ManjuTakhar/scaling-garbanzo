from sqlalchemy import Column, String, ForeignKey, TIMESTAMP, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.core.utils import generate_id, generate_alphanumeric_id

class IssueActivity(Base):
    """
    Model for tracking activity on issues, including:
    - Status changes
    - Assignee changes
    - Label additions/removals
    - Comments
    - Field updates
    """
    __tablename__ = "issue_activities"
    
    id = Column(String, primary_key=True)
    issue_id = Column(String, ForeignKey("issues.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    activity_type = Column(String, nullable=False)  # STATUS_CHANGE, ASSIGNEE_CHANGE, LABEL_ADDED, etc.
    old_value = Column(JSON, nullable=True)  # Store previous value if applicable
    new_value = Column(JSON, nullable=True)  # Store new value if applicable
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    issue = relationship("Issue", backref="activities")
    user = relationship("User", foreign_keys=[user_id])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = f"act-{generate_alphanumeric_id()}"


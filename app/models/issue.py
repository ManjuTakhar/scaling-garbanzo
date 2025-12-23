from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..db.base import Base
from app.core.utils import generate_id, generate_alphanumeric_id
from sqlalchemy import TIMESTAMP
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB
import random
import string

class Issue(Base):
    """
    Issue model representing a work item that can be part of an epic or have sub-issues.
    
    Relationships and Behavior:
    - Issues can be optionally associated with one epic (many-to-one relationship)
    - Issues can have multiple sub-issues (self-referential relationship)
    - An issue can be a parent to other issues (e.g., a story containing tasks)
    - An issue can be a child of another issue (e.g., a task belonging to a story)
    - An issue can be a child of an epic (optional)
    """
    __tablename__ = "issues"
    id = Column(String, primary_key=True)
    display_id = Column(String, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(JSONB, nullable=True)
    acceptance_criteria = Column(JSONB, nullable=True)
    status = Column(String(20), default="TODO")
    priority = Column(String(20), default="MEDIUM")
    issue_type = Column(String(20), default="FEATURE")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    start_date = Column(TIMESTAMP(timezone=True), nullable=True)
    due_date = Column(TIMESTAMP(timezone=True), nullable=True)
    parent_issue_id = Column(String, ForeignKey("issues.id"), nullable=True)
    story_points = Column(Integer, nullable=True)
    cycle_id = Column(String, ForeignKey("cycles.id"), nullable=True)
    # epic_id = Column(String, ForeignKey("epics.id"), nullable=True)  # Commented out since Epic table doesn't exist
    created_by = Column(String, ForeignKey("users.user_id"), nullable=False)
    updated_by = Column(String, ForeignKey("users.user_id"), nullable=True)
    assignee = Column(String, ForeignKey("users.user_id"), nullable=True)
    team_id = Column(String, ForeignKey("teams.team_id"), nullable=True)
    
    # Archiving fields
    is_archived = Column(String, default="false")  # "true" or "false" as string for consistency
    archived_at = Column(TIMESTAMP(timezone=True), nullable=True)
    archived_by = Column(String, ForeignKey("users.user_id"), nullable=True)
    archive_reason = Column(Text, nullable=True)  # Optional reason for archiving
    
    # Self-referential relationship for sub-issues only
    sub_issues = relationship("Issue", backref="parent_issue", remote_side=[id])

    cycle = relationship("Cycle", back_populates="issues")
    team = relationship("Team", back_populates="issues")
    created_by_user = relationship("User", foreign_keys=[created_by])
    updated_by_user = relationship("User", foreign_keys=[updated_by])
    assignee_user = relationship("User", foreign_keys=[assignee])
    archived_by_user = relationship("User", foreign_keys=[archived_by])
    labels = relationship("Label", secondary="issue_labels", back_populates="issues", lazy="joined")
    issue_labels = relationship("IssueLabel", back_populates="issue", lazy="joined", overlaps="labels")
    # epic = relationship("Epic", backref="issues")  # Commented out since Epic model doesn't exist

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = generate_id(kwargs.get('title', ''))

    def update(self, **kwargs):
        """Update project attributes with provided values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self


class TeamIssueSequence(Base):
    __tablename__ = 'team_issue_sequences'

    id = Column(String, primary_key=True, default=generate_alphanumeric_id)
    team_id = Column(String, ForeignKey('teams.team_id'), nullable=False)
    sequence_number = Column(Integer, default=0, nullable=False)


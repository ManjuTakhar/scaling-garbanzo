import enum
import random
import string
from sqlalchemy import Column, String, Text, Enum, Integer, Date, TIMESTAMP, func, CheckConstraint, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base
from sqlalchemy.orm import relationship
from app.utils.utils import generate_custom_id

class StatusEnum(str, enum.Enum):
    On_Track = "On Track"
    At_Risk = "At Risk"
    Blocked = "Blocked"
    Completed = "Completed"

    def _get_value(self):
        return self.value

    def __str__(self):
        return self.value

class StageEnum(str, enum.Enum):
    Planning = "Planning"
    Shaping = "Shaping"
    Delivered = "Delivered"

def generate_project_id(title: str) -> str:
    words = title.split()
    initials = ''.join(word[0].upper() for word in words if word.isalnum())[:3]
    alphanumeric = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"{initials}-{alphanumeric}"


class Project(Base):
    __tablename__ = "projects"
    project_id = Column(String, primary_key=True)
    initiative_id = Column(String, ForeignKey("initiatives.initiative_id"), nullable=True)
    workspace_id = Column(String, ForeignKey("workspaces.workspace_id"), nullable=False)
    title = Column(String(255), nullable=False)
    short_description = Column(String(255), nullable=True)
    description = Column(JSONB, nullable=True)
    status = Column(String(50), nullable=True)
    stage = Column(String(50), nullable=True)
    progress = Column(Integer, CheckConstraint('progress >= 0 AND progress <= 100'), nullable=True)
    dri_id = Column(String, ForeignKey("users.user_id"), nullable=True)
    start_date = Column(TIMESTAMP(timezone=True), nullable=True)
    end_date = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_updated = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    priority = Column(String(50), nullable=True)

    # Relationships
    initiative = relationship("Initiative", back_populates="projects")
    teams = relationship("Team", secondary="project_teams", back_populates="projects")
    dri = relationship("User")
    workspace = relationship("Workspace")
    channels = relationship("Channel", secondary="project_channels", back_populates="projects")
    milestones = relationship("Milestone", back_populates="project")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.project_id:
            self.project_id = generate_custom_id(kwargs.get('title', ''))

    def update(self, **kwargs):
        """Update project attributes with provided values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self


class Milestone(Base):
    __tablename__ = "milestones"
    milestone_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False)
    title = Column(String, nullable=False)
    dri = Column(String, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    target_date = Column(TIMESTAMP(timezone=True), nullable=True)
    status = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_updated = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    created_by = relationship("User",foreign_keys=[dri])
    project = relationship("Project", back_populates="milestones")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.milestone_id:
            self.milestone_id = generate_custom_id(kwargs.get('title', ''))

    def update(self, **kwargs):
        """Update milestone attributes with provided values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

import enum
import random
import string
from sqlalchemy import Column, String, Integer, TIMESTAMP, Date, CheckConstraint, func, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.initiative_teams import initiative_teams  # Import the association table
from app.utils.utils import generate_custom_id

class StatusEnum(str, enum.Enum):
    On_Track = "On Track"
    At_Risk = "At Risk"
    Blocked = "Blocked"
    Completed = "Completed"

class Initiative(Base):
    __tablename__ = "initiatives"
    initiative_id = Column(String, primary_key=True)
    title = Column(String(255), nullable=False)
    short_description = Column(String(255), nullable=True)
    description = Column(JSONB, nullable=True)
    owner_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    status = Column(String(50), nullable=True)
    progress = Column(Integer, CheckConstraint('progress >= 0 AND progress <= 100'))
    start_date = Column(TIMESTAMP(timezone=True), nullable=True)
    end_date = Column(TIMESTAMP(timezone=True), nullable=True)  
    workspace_id = Column(String, ForeignKey("workspaces.workspace_id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_updated = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    priority = Column(String(50), nullable=True)

    # Relationships
    projects = relationship("Project", back_populates="initiative")  # One-to-many relationship with Project
    teams = relationship("Team", secondary="initiative_teams", back_populates="initiatives")  # Many-to-many relationship with Team
    workspace = relationship("Workspace")  # Relationship to Tenant
    owner = relationship("User")  # Relationship to User (Owner)
    channels = relationship("Channel", secondary="initiative_channels", back_populates="initiatives")  # Many-to-many relationship with Channel
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.initiative_id:
            self.initiative_id = generate_custom_id(kwargs.get('title', ''))

    def update(self, **kwargs):
        """Update initiative attributes with provided values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

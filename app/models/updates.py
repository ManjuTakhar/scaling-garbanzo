import random
import string
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base
from sqlalchemy.orm import relationship
def generate_update_id(prefix: str) -> str:
    alphanumeric = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"{prefix}-{alphanumeric}"

class ProjectUpdate(Base):
    __tablename__ = "project_updates"
    update_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False)
    content = Column(JSONB, nullable=False)
    created_by = Column(String, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    current_status = Column(String, nullable=True, default="")  # Added current project status column

    posted_by = relationship("User", foreign_keys=[created_by])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.update_id:
            self.update_id = generate_update_id("PU")

    def update(self, **kwargs):
        """Update project update attributes with provided values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

class InitiativeUpdate(Base):
    __tablename__ = "initiative_updates"
    update_id = Column(String, primary_key=True)
    initiative_id = Column(String, ForeignKey('initiatives.initiative_id', ondelete='CASCADE'), nullable=False)
    content = Column(JSONB, nullable=False)
    created_by = Column(String, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    current_status = Column(String, nullable=True)  # Added current initiative status column
    
    posted_by = relationship("User")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.update_id:
            self.update_id = generate_update_id("IU")

    def update(self, **kwargs):
        """Update initiative update attributes with provided values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self
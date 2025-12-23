import random
import string
from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey, func, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base

def generate_resource_id() -> str:
    alphanumeric = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"RES-{alphanumeric}"

class ProjectResource(Base):
    __tablename__ = "project_resources"
    resource_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False)
    title = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)
    created_by = Column(String, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    pinned = Column(Boolean, default=False)

    created_by_user = relationship("User", foreign_keys=[created_by])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.resource_id:
            self.resource_id = generate_resource_id() 

    def update(self, **kwargs):
        """Update resource attributes with provided values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

class InitiativeResource(Base):
    __tablename__ = "initiative_resources"
    resource_id = Column(String, primary_key=True)
    initiative_id = Column(String, ForeignKey('initiatives.initiative_id', ondelete='CASCADE'), nullable=False)
    title = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)
    created_by = Column(String, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    pinned = Column(Boolean, default=False)
    created_by_user = relationship("User", foreign_keys=[created_by])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.resource_id:
            self.resource_id = generate_resource_id() 

    def update(self, **kwargs):
        """Update resource attributes with provided values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self
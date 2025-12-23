from sqlalchemy import Column, String, ForeignKey, TIMESTAMP, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
from sqlalchemy.sql import func
from uuid import uuid4
from pydantic import BaseModel
from typing import Optional, List
from app.dto.dtos import UserDTO
import enum

class DependencyType(enum.Enum):
    DEPENDS_ON = "depends_on"
    DEPENDENCY_OF = "dependency_of"

class InitiativeDependency(Base):
    __tablename__ = "initiative_dependencies"
    
    dependency_id = Column(String, primary_key=True)
    type = Column(Enum(DependencyType), nullable=False)
    source_initiative_id = Column(String, ForeignKey("initiatives.initiative_id"), nullable=False)
    target_initiative_id = Column(String, ForeignKey("initiatives.initiative_id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(String, ForeignKey("users.user_id"), nullable=False)
    updated_by = Column(String, ForeignKey("users.user_id"), nullable=True)
    status = Column(String, nullable=False, default="active")
    description = Column(String, nullable=True)
    
    # Relationships
    source_initiative = relationship("Initiative", foreign_keys=[source_initiative_id])
    target_initiative = relationship("Initiative", foreign_keys=[target_initiative_id])
    created_by_user = relationship("User", foreign_keys=[created_by])
    updated_by_user = relationship("User", foreign_keys=[updated_by])

class ProjectDependency(Base):
    __tablename__ = "project_dependencies"
    
    dependency_id = Column(String, primary_key=True)
    type = Column(Enum(DependencyType), nullable=False)
    source_project_id = Column(String, ForeignKey("projects.project_id"), nullable=False)
    target_project_id = Column(String, ForeignKey("projects.project_id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(String, ForeignKey("users.user_id"), nullable=False)
    updated_by = Column(String, ForeignKey("users.user_id"), nullable=True)
    status = Column(String, nullable=False, default="active")
    description = Column(String, nullable=True)
    
    # Relationships
    source_project = relationship("Project", foreign_keys=[source_project_id])
    target_project = relationship("Project", foreign_keys=[target_project_id])
    created_by_user = relationship("User", foreign_keys=[created_by])
    updated_by_user = relationship("User", foreign_keys=[updated_by])
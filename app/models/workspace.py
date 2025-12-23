from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.utils.utils import generate_custom_id
# Ensure WorkspaceInvitation is imported so SQLAlchemy can resolve the relationship
from app.models.workspace_invitation import WorkspaceInvitation  # noqa: F401

class Workspace(Base):
    __tablename__ = "workspaces"

    workspace_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    tenant_id = Column(String, ForeignKey('tenants.tenant_id'), nullable=False)
    created_by = Column(String, ForeignKey('users.user_id'), nullable=False)
    description = Column(Text, nullable=True)
    settings = Column(Text, nullable=True)  # JSON string for workspace settings
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="workspaces")
    users = relationship("User", foreign_keys="User.workspace_id", back_populates="workspace")
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    teams = relationship("Team", back_populates="workspace", cascade="all, delete-orphan")
    channels = relationship("Channel", back_populates="workspace", cascade="all, delete-orphan")
    invitations = relationship("WorkspaceInvitation", back_populates="workspace", cascade="all, delete-orphan")


    def __init__(self, name: str, tenant_id: str, created_by: str, **kwargs):
        self.name = name
        self.tenant_id = tenant_id
        self.created_by = created_by
        super().__init__(**kwargs)
        self.workspace_id = f"WSP-{generate_custom_id(name)}"

class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

    workspace_id = Column(String, ForeignKey("workspaces.workspace_id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    role = Column(String, nullable=False, default="Member")  # Owner, Admin, Member
    joined_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    workspace = relationship("Workspace", back_populates="members")

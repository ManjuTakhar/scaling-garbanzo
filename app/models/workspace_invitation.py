from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class WorkspaceInvitation(Base):
    __tablename__ = "workspace_invitations"
    
    invitation_id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.workspace_id", ondelete="CASCADE"), nullable=False)
    email = Column(String, nullable=False)
    invited_by = Column(String, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True)
    role = Column(String, nullable=False, default="Member")  # "Admin" | "Member"
    magic_token = Column(String, nullable=False, unique=True)
    is_accepted = Column(Boolean, nullable=False, default=False)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    accepted_at = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Relationships
    workspace = relationship("Workspace", back_populates="invitations")
    inviter = relationship("User", foreign_keys=[invited_by])
    
    def __repr__(self):
        return f"<WorkspaceInvitation(invitation_id={self.invitation_id}, email={self.email}, workspace_id={self.workspace_id})>"

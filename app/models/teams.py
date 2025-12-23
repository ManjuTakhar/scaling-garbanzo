from sqlalchemy import Column, String, ForeignKey, TIMESTAMP, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.utils.utils import generate_custom_id
from app.models.initiative_teams import initiative_teams  # Import the association table

class Team(Base):
    __tablename__ = "teams"

    team_id = Column(String, primary_key=True)  # ✅ Ensure correct UUID handling
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    workspace_id = Column(String, ForeignKey("workspaces.workspace_id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    priority = Column(Integer, nullable=False, default=5)
    settings = Column(Text, nullable=True)

    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    workspace = relationship("Workspace", back_populates="teams")
    initiatives = relationship("Initiative", secondary=initiative_teams, back_populates="teams")
    projects = relationship("Project", secondary="project_teams", back_populates="teams")
    channels = relationship("Channel", back_populates="team")
    issues = relationship("Issue", back_populates="team")
    cycles = relationship("Cycle", back_populates="team")
    
    def __init__(self, name: str, **kwargs):
        self.name = name
        super().__init__(**kwargs)
        self.team_id = f"TEAM-{generate_custom_id(name)}"  # Generate custom ID based on the entity name 

class TeamMember(Base):
    __tablename__ = "team_members"

    team_id = Column(String, ForeignKey("teams.team_id", ondelete="CASCADE"), primary_key=True)  # ✅ Ensure UUID
    user_id = Column(String, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)  # ✅ Ensure UUID
    added_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    team = relationship("Team", back_populates="members")
    user = relationship("User")

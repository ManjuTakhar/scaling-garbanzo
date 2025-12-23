from sqlalchemy import Column, String, Boolean, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Channel(Base):
    __tablename__ = "channels"

    channel_id = Column(String, primary_key=True)  # Slack channel ID
    name = Column(String, nullable=False)    # Channel name
    is_channel = Column(Boolean, default=True)  # Is it a channel?
    is_private = Column(Boolean, default=False)  # Is it private?
    created = Column(Integer)  # Created timestamp
    is_archived = Column(Boolean, default=False)  # Is it archived?
    is_general = Column(Boolean, default=False)  # Is it the general channel?
    creator = Column(String)  # Creator user ID
    purpose = Column(Text)  # Purpose of the channel
    topic = Column(Text)  # Topic of the channel
    num_members = Column(Integer)  # Number of members
    team_id = Column(String, ForeignKey('teams.team_id'), nullable=True)  # Team ID (context_team_id)
    workspace_id = Column(String, ForeignKey('workspaces.workspace_id'), nullable=False)  # Foreign key reference to workspaces

    # You can add relationships if needed 
    team = relationship("Team", back_populates="channels")  # Update relationship 
    workspace = relationship("Workspace", foreign_keys=[workspace_id], back_populates="channels") 
    initiatives = relationship("Initiative", secondary="initiative_channels", back_populates="channels")  # Many-to-many relationship with Initiative
    projects = relationship("Project", secondary="project_channels", back_populates="channels")  # Many-to-many relationship with Project
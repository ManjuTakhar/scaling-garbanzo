from sqlalchemy import Column, String, ForeignKey
from app.db.base import Base

class ProjectChannel(Base):
    __tablename__ = "project_channels"
    
    project_id = Column(String, ForeignKey('projects.project_id', ondelete='CASCADE'), primary_key=True)
    channel_id = Column(String, ForeignKey('channels.channel_id', ondelete='CASCADE'), primary_key=True)

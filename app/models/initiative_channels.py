from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class InitiativeChannel(Base):
    __tablename__ = "initiative_channels"
    
    initiative_id = Column(String, ForeignKey('initiatives.initiative_id', ondelete='CASCADE'), primary_key=True)
    channel_id = Column(String, ForeignKey('channels.channel_id', ondelete='CASCADE'), primary_key=True)
from sqlalchemy import Column, String, TIMESTAMP, Float, Integer
from sqlalchemy.orm import relationship
from ..db.base import Base
from app.core.utils import generate_id, generate_alphanumeric_id
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func

class Cycle(Base):
    __tablename__ = "cycles"

    id = Column(String, primary_key=True)
    display_id = Column(String, nullable=False)
    name = Column(String(100), nullable=False)
    status = Column(String(20), default="ACTIVE")
    start_date = Column(TIMESTAMP(timezone=True), nullable=False)
    due_date = Column(TIMESTAMP(timezone=True), nullable=False)
    completed_at = Column(TIMESTAMP(timezone=True), nullable=True)  
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    started_by = Column(String, ForeignKey("users.user_id"), nullable=True)
    completed_by = Column(String, ForeignKey("users.user_id"), nullable=True)
    number = Column(Float, nullable=True)  
    created_by = Column(String, ForeignKey("users.user_id"), nullable=True)
    updated_by = Column(String, ForeignKey("users.user_id"), nullable=True)
    team_id = Column(String, ForeignKey("teams.team_id"), nullable=False)
    description = Column(String, nullable=True)

    # Relationship to link cycles to issues
    issues = relationship("Issue", back_populates="cycle")
    team = relationship("Team", back_populates="cycles")

    created_by_user = relationship("User", foreign_keys=[created_by])
    updated_by_user = relationship("User", foreign_keys=[updated_by])
    completed_by_user = relationship("User", foreign_keys=[completed_by])
    started_by_user = relationship("User", foreign_keys=[started_by])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = generate_id(kwargs.get('name', ''))


class TeamCycleSequence(Base):
    __tablename__ = 'team_cycle_sequences'

    id = Column(String, primary_key=True, default=generate_alphanumeric_id)
    team_id = Column(String, ForeignKey('teams.team_id'), nullable=False)
    sequence_number = Column(Integer, default=0, nullable=False)


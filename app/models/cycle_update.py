from sqlalchemy import Column, String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.utils import generate_id
from app.db.base import Base

class CycleUpdate(Base):
    __tablename__ = "cycle_updates"
    id = Column(String, primary_key=True)
    cycle_id = Column(String, ForeignKey('cycles.id', ondelete='CASCADE'), nullable=False)
    content = Column(JSONB, nullable=False)
    created_by = Column(String, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(String, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)

    posted_by = relationship("User", foreign_keys=[created_by])
    updated_by_user = relationship("User", foreign_keys=[updated_by])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = generate_id("CU")

    def update(self, **kwargs):
        """Update cycle update attributes with provided values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self


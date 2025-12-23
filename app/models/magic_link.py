from sqlalchemy import Column, String, Boolean, TIMESTAMP, func
from sqlalchemy.sql import func
from app.db.base import Base
from datetime import datetime, timezone


class MagicLink(Base):
    """Model for storing magic link tokens for passwordless authentication"""
    __tablename__ = "magic_links"
    
    token_id = Column(String, primary_key=True)
    email = Column(String, nullable=False, index=True)
    token_hash = Column(String, nullable=False, unique=True)  # Hashed version of the JWT token
    is_used = Column(Boolean, nullable=False, default=False)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    used_at = Column(TIMESTAMP(timezone=True), nullable=True)
    purpose = Column(String, nullable=False, default="login")  # "login", "signup", "invite"
    workspace_id = Column(String, nullable=True)  # Optional workspace context

















from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
import random
import string
from sqlalchemy.dialects.postgresql import TIMESTAMP

def generate_comment_id(content: str) -> str:
    # Get initials from content (up to 3 characters)
    words = content.split()
    initials = ''.join(word[0].upper() for word in words if word)[:3]
    
    # Generate 10 character alphanumeric string
    alphanumeric = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    # Combine with a hyphen
    return f"{initials}-{alphanumeric}"

class InitiativeComment(Base):
    __tablename__ = "initiative_comments"
    
    comment_id = Column(String, primary_key=True)
    content = Column(String, nullable=False)
    created_by = Column(String, ForeignKey("users.user_id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    update_id = Column(String, ForeignKey("initiative_updates.update_id"))

    created_by_user = relationship("User", foreign_keys=[created_by])
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.comment_id:
            self.comment_id = generate_comment_id(kwargs.get('content', ''))

    def update(self, **kwargs):
        """Update initiative attributes with provided values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

def generate_reaction_id(reaction: str = 'Reaction') -> str:
    words = reaction.split()
    initials = ''.join(word[0].upper() for word in words if word)[:3]
    
    # Generate 10 character alphanumeric string
    alphanumeric = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    # Combine with a hyphen
    return f"{initials}-{alphanumeric}"

class InitiativeReaction(Base):
    __tablename__ = "initiative_reactions"
    
    reaction_id = Column(String, primary_key=True)
    update_id = Column(String, ForeignKey("initiative_updates.update_id"))
    reacted_by = Column(String, ForeignKey("users.user_id"), nullable=False)
    reaction_type = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    reacted_by_user = relationship("User", foreign_keys=[reacted_by])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.reaction_id:
            self.reaction_id = generate_reaction_id(kwargs.get('reaction_type', ''))

    def update(self, **kwargs):
        """Update initiative attributes with provided values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

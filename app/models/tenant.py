from sqlalchemy import Column, String, TIMESTAMP, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.utils.utils import generate_custom_id  # Import the utility function

class Tenant(Base):
    __tablename__ = "tenants"

    tenant_id = Column(String, primary_key=True)  # Custom ID
    name = Column(String, nullable=False)
    contact_person = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    website = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    size = Column(String, nullable=True)
    tax_id = Column(String, nullable=True)
    billing_address = Column(String, nullable=True)
    slack_bot_token = Column(Text, nullable=True)  # Encrypted Slack bot token
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_updated = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Establish relationship with User
    users = relationship("User", back_populates="tenant")
    
    # Establish relationship with Workspace
    workspaces = relationship("Workspace", back_populates="tenant")

    def __init__(self, name: str, **kwargs):
        self.name = name
        super().__init__(**kwargs)
        self.tenant_id = f"STR-{generate_custom_id(name)}"  # Generate custom ID based on the entity name 
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.utils.utils import generate_custom_id

class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    role = Column(String, nullable=True)  # Consider using an Enum for roles
    picture = Column(String, nullable=True)
    tenant_id = Column(String, ForeignKey('tenants.tenant_id'), nullable=False)
    # Allow user creation before onboarding creates a workspace
    workspace_id = Column(String, ForeignKey('workspaces.workspace_id'), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_updated = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(TIMESTAMP(timezone=True), nullable=True)

    # Establish relationship with Tenant
    tenant = relationship("Tenant", back_populates="users")  # Ensure this line is present
    
    # Establish relationship with Workspace (using direct foreign key)
    workspace = relationship("Workspace", foreign_keys=[workspace_id], back_populates="users")

    def __init__(self, name: str, **kwargs):
        self.name = name
        super().__init__(**kwargs)
        self.user_id = f"USR-{generate_custom_id(name)}"  # Generate custom ID based on the entity name 

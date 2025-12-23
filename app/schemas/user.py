from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None  # Use EmailStr for email validation
    role: Optional[str] = None  # Optional role field
    picture: Optional[str] = None  # Optional picture field
    tenant_id: str
    # Workspace may be assigned after onboarding
    workspace_id: Optional[str] = None

class UserCreate(UserBase):
    """Schema for creating a new user"""
    pass

class UserUpdate(UserBase):
    """Schema for updating an existing user"""
    pass

class User(UserBase):
    user_id: str
    created_at: Optional[int] = None
    last_login: Optional[int] = None

    class Config:
        orm_mode = True

class UserResponse(UserBase):
    """Schema for returning user details"""
    user_id: str  # Include user_id in the response
    created_at: Optional[int] = None  # Timestamp
    last_updated: Optional[int] = None  # Timestamp
    onboarding_completed: Optional[bool] = None

    class Config:
        orm_mode = True  # Enable ORM mode for compatibility with SQLAlchemy models
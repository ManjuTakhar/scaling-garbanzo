from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserAuth(BaseModel):
    email: EmailStr
    name: str
    picture: Optional[str] = None
    role: str = "USER"  # Default role as string

    class Config:
        orm_mode = True

class Token(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema for token payload"""
    email: Optional[str] = None

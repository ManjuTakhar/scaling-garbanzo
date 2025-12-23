from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class MagicLinkCreate(BaseModel):
    email: EmailStr
    purpose: str = "login"  # "login", "signup", "invite"
    workspace_id: Optional[str] = None


class MagicLinkResponse(BaseModel):
    token_id: str
    email: str
    expires_at: int
    purpose: str
    workspace_id: Optional[str] = None
    is_valid: bool = True


class MagicLinkVerify(BaseModel):
    token: str


class MagicLinkSend(BaseModel):
    email: EmailStr
    purpose: str = "login"
    workspace_id: Optional[str] = None

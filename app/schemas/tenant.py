from pydantic import BaseModel
from typing import Optional


class TenantBase(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    tax_id: Optional[str] = None
    billing_address: Optional[str] = None

class TenantCreate(TenantBase):
    """Schema for creating a new tenant"""
    pass

class TenantResponse(BaseModel):
    """Response model for returning tenant details"""
    tenant_id: str
    name: str
    created_at: Optional[int] = None  # Timestamp

    class Config:
        from_attributes = True  # This enables ORM model -> Pydantic model conversion 

class TenantUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    tax_id: Optional[str] = None
    billing_address: Optional[str] = None 
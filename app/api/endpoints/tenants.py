from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.tenant import TenantCreate, TenantResponse
from app.crud.tenant import create_tenant, update_tenant, delete_tenant
from app.crud import tenant as crud
from app.services.slack_service import SlackService
from app.schemas.channel import ChannelResponse
from typing import List

router = APIRouter()

@router.post("/tenants/", response_model=TenantResponse)
def create_tenant_endpoint(tenant: TenantCreate, db: Session = Depends(get_db)):
    """Create a new tenant."""
    return create_tenant(db, tenant)

@router.put("/tenants{tenant_id}", response_model=TenantResponse)
def update_tenant_endpoint(tenant_id: str, tenant: TenantCreate, db: Session = Depends(get_db)):
    """Update an existing tenant."""
    updated_tenant = update_tenant(db, tenant_id, tenant)
    if not updated_tenant:
        raise HTTPException(status_code=401, detail="Tenant not found")
    return updated_tenant

@router.delete("/tenants/{tenant_id}", response_model=dict)
def delete_tenant_endpoint(tenant_id: str, db: Session = Depends(get_db)):
    """Delete a tenant."""
    result = delete_tenant(db, tenant_id)
    if not result:
        raise HTTPException(status_code=401, detail="Tenant not found")
    return {"detail": "Tenant deleted successfully"}

@router.get("/tenants", response_model=list[TenantResponse])
def list_tenants_api(db: Session = Depends(get_db)):
    """API endpoint to list all tenants."""
    return crud.get_all_tenants(db=db)

@router.get("/tenants/{tenant_id}/channels/refresh")
async def refresh_channels(tenant_id: str, db: Session = Depends(get_db), 
                           authorization: str = Header(...)):
    """API endpoint to fetch all channels for a specific tenant."""
    try:
        slack_service = SlackService(db=db)
        print(f"Refreshing channels for tenant {tenant_id}")
        channels = slack_service.refresh_channels(tenant_id, authorization)
        return {"message": "Channels refreshed and stored successfully", "channels": channels}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Additional endpoints for managing tenants can be added here 
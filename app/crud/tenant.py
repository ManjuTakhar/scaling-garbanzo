from sqlalchemy.orm import Session
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse

def create_tenant(db: Session, tenant: TenantCreate) -> TenantResponse:
    """Create a new tenant in the database."""
    
    # Create the tenant with explicit name setting
    db_tenant = Tenant(
        name=tenant.name,  # Explicitly set name
        contact_person=tenant.contact_person,
        contact_email=tenant.contact_email,
        contact_phone=tenant.contact_phone,
        address=tenant.address,
        website=tenant.website,
        industry=tenant.industry,
        size=tenant.size,
        tax_id=tenant.tax_id,
        billing_address=tenant.billing_address
    )
    
    # Debug print to see what's being sent to the database
    print("DB tenant object:", db_tenant.__dict__)
    
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)

    # Convert datetime fields to epoch time
    
    return TenantResponse(
        tenant_id=db_tenant.tenant_id,
        name=db_tenant.name,
        created_at=int(db_tenant.created_at.timestamp()) if db_tenant.created_at else None  # Convert to timestamp
    )

def update_tenant(db: Session, tenant_id: str, update: TenantUpdate) -> Tenant:
    """Update an existing tenant in the database."""
    db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not db_tenant:
        return None  # Tenant not found

    # Use Pydantic's exclude_unset to only update provided fields
    update_data = update.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_tenant, key, value)  # Update only the fields that are provided

    db.commit()
    db.refresh(db_tenant)

    # Convert datetime fields to epoch time for the response
    return {
        "tenant_id": db_tenant.tenant_id,
        "name": db_tenant.name,
        "contact_person": db_tenant.contact_person,
        "contact_email": db_tenant.contact_email,
        "contact_phone": db_tenant.contact_phone,
        "address": db_tenant.address,
        "website": db_tenant.website,
        "industry": db_tenant.industry,
        "size": db_tenant.size,
        "tax_id": db_tenant.tax_id,
        "billing_address": db_tenant.billing_address,
        "created_at": int(db_tenant.created_at.timestamp()),  # Convert to epoch time
        "last_updated": int(db_tenant.last_updated.timestamp())  # Convert to epoch time
    }

def delete_tenant(db: Session, tenant_id: str) -> bool:
    """Delete a tenant from the database."""
    db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not db_tenant:
        return False  # Tenant not found

    db.delete(db_tenant)
    db.commit()
    return True 

def get_all_tenants(db: Session):
    """Fetch all tenants."""
    tenants = db.query(Tenant).all()
    return [
        TenantResponse(
            tenant_id=str(tenant.tenant_id),
            name=tenant.name,
            created_at=int(tenant.created_at.timestamp()) if tenant.created_at else None  # Convert to timestamp
        )
        for tenant in tenants
    ] 

def get_encrypted_slack_token_for_tenant(db: Session, tenant_id: str) -> str:
    """Fetch the encrypted Slack bot token for a specific tenant."""
    db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not db_tenant:
        return None 
    return db_tenant.slack_bot_token 

def add_slack_token(db: Session, tenant_id: str, encrypted_token: str) -> bool:
    """Add the Slack bot token for a specific tenant."""
    db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not db_tenant:
        return False  # Tenant not found

    db_tenant.slack_bot_token = encrypted_token
    db.commit()  # Commit the changes to save the token
    return True  # Indicate success 
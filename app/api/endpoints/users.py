from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse
from app.crud import user as crud
from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from fastapi import Query
from app.schemas.user import UserCreate
from app.crud.user import create_user  # Assuming you have a create_user function in your CRUD module
from app.crud.user import set_user_workspace_id
from google.oauth2 import id_token
from google.auth.transport import requests
from app.schemas.tenant import TenantCreate
from app.crud.tenant import create_tenant
from app.core.config import settings
from jose import jwe
from app.auth.token_decoder import AuthJSDecoder
from app.api.dependencies import get_current_user, get_current_user_with_workspace
from app.models.workspace import WorkspaceMember

router = APIRouter()

@router.post("/users", response_model=UserResponse)
def create_user_api(user: UserCreate, db: Session = Depends(get_db)):
    """API endpoint to create a new user."""
    return crud.create_user(db=db, user=user)

@router.get("/users", response_model=list[UserResponse])
async def get_all_users_api(
    request: Request,
    db: Session = Depends(get_db), 
    authorization: str = Header(...),
    team_id: Optional[str] = Query(None),
    user_context: dict = Depends(get_current_user_with_workspace)
):
    """API to get all users - filtered by workspace/tenant for data isolation."""
    return crud.get_all_users(
        db,
        team_id=team_id,
        workspace_id=user_context["workspace_id"]
    )


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_api(user_id: str, db: Session = Depends(get_db), 
                 authorization: str = Header(...),
                 current_user: dict = Depends(get_current_user)):
    """API endpoint to fetch a single user by user_id."""
    print(f"current_user: {current_user}")
    user = crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    user = crud.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.get("/initialize", response_model=UserResponse)
def initialize_user(request: Request, authorization: str = Header(...), 
                    current_user: dict = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    """Register a new user using the Google OAuth token."""
    try:
        # Verify the token
        user_details = current_user
        # create tenant when user is registered 
        # TODO: Use existing tenant if it's domain exists in the database 
        # TODO: As of now, we are creating a new tenant for each user

        try:
            user = crud.get_user_by_email(db, user_details["email"])
        except Exception as e:
            # If user lookup fails due to SQLAlchemy issues, treat as no user found
            print(f"User lookup failed: {e}")
            user = None
            
        if not user:
            # Only create tenant and user if user doesn't exist
            # TODO: Consider using domain-based tenant sharing in the future
            tenant_data = TenantCreate(
                name=user_details["name"]
            )
            tenant = create_tenant(db, tenant_data)
            # Prepare user data for creation
            user_data = UserCreate(
                email=user_details["email"],
                name=user_details["name"],
                picture=user_details["picture"],
                role="Engineer",  # Set a default role or modify as needed
                tenant_id=tenant.tenant_id
            )
            user = create_user(db, user_data)
        # If user exists, use the existing user (no new tenant creation)
        # Determine onboarding completion: if user has a tenant_id and at least one workspace membership
        onboarding_completed = False
        try:
            if user and user.tenant_id:
                # Check membership
                membership = db.query(WorkspaceMember).filter(WorkspaceMember.user_id == user.user_id).first()
                onboarding_completed = membership is not None
        except Exception:
            onboarding_completed = bool(user and user.tenant_id)

        # Attach flag and workspace_id to user response
        if isinstance(user, dict):
            user["onboarding_completed"] = onboarding_completed
            try:
                # Prefer actual membership workspace, else default
                user["workspace_id"] = membership.workspace_id if onboarding_completed and membership else None
            except Exception:
                user["workspace_id"] = None
            return user
        # If it's a Pydantic model, set the field and return
        try:
            user.onboarding_completed = onboarding_completed
            try:
                user.workspace_id = membership.workspace_id if onboarding_completed and membership else None
                # Backfill workspace_id on the user record if missing
                if onboarding_completed and membership and not getattr(user, "workspace_id", None):
                    try:
                        set_user_workspace_id(db, user.user_id, membership.workspace_id)
                    except Exception:
                        pass
            except Exception:
                user.workspace_id = None
        except Exception:
            user = UserResponse(**user.dict(exclude={"onboarding_completed"}))
            user.onboarding_completed = onboarding_completed
            try:
                user.workspace_id = membership.workspace_id if onboarding_completed and membership else None
            except Exception:
                user.workspace_id = None
        return user
    
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")
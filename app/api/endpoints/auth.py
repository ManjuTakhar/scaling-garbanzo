from fastapi import APIRouter, Depends, HTTPException, Request, status
from httpx import AsyncClient
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.schemas.auth import Token, UserAuth
from app.crud.user import create_or_update_user, get_user_by_email
from app.db.session import get_db
from jose import jwt, JWTError
from app.api.deps import get_current_user
from typing import Optional
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["auth"])

# Create a schema for refresh token request
class RefreshRequest(BaseModel):
    refresh_token: str

@router.get("/login/google")
async def google_login():
    """Generate Google login URL"""
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "access_type": "offline",
        "prompt": "consent",
    }
    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    return {"url": f"{settings.GOOGLE_AUTH_URL}?{query_string}"}

@router.get("/callback/google")
async def google_callback(
    code: str,
    scope: str,
    authuser: Optional[str] = None,
    hd: Optional[str] = None,  # hosted domain (for Google Workspace)
    prompt: Optional[str] = None,
    db = Depends(get_db)
):
    """Handle Google OAuth callback"""
    # Verify hosted domain if needed
    if hd and hd != "synchrone.ai":
        raise HTTPException(
            status_code=400,
            detail="Invalid hosted domain. Please use your Synchrone email."
        )

    async with AsyncClient() as client:
        # Exchange code for token
        token_response = await client.post(
            settings.GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            }
        )
        
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get token")
            
        tokens = token_response.json()
        
        # Get user info
        user_response = await client.get(
            settings.GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        
        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")
            
        user_info = user_response.json()
        
        # Verify email domain if needed
        email_domain = user_info["email"].split("@")[1]
        if email_domain != "synchrone.ai" and email_domain != "gmail.com":
            raise HTTPException(
                status_code=400,
                detail="Please use your Synchrone email address or a personal Google account."
            )
        
        # Create or update user
        user_data = UserAuth(
            email=user_info["email"],
            name=user_info["name"],
            picture=user_info.get("picture")
        )
        user = create_or_update_user(db, user_data)
        
        # Create tokens
        access_token = create_access_token(data={"sub": user.email})
        refresh_token = create_refresh_token(data={"sub": user.email})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

@router.post("/refresh")
async def refresh_token(request: RefreshRequest):
    """Get new access token using refresh token"""
    try:
        # Verify refresh token specifically
        token_data = verify_token(request.refresh_token, token_type="refresh")
        if not token_data or not token_data.email:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
            
        # Create new access token
        new_access_token = create_access_token(data={"sub": token_data.email})
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.get("/test-auth")
async def test_authentication(current_user = Depends(get_current_user)):
    """Test route to verify authentication"""
    return {
        "message": "Authentication successful",
        "user": {
            "email": current_user.email,
            "name": current_user.name
        }
    }

@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Token endpoint for Swagger UI authorization"""
    user = get_user_by_email(db, email=form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
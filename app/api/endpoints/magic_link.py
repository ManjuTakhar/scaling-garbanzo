from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.crud import magic_link as crud_magic_link
from app.crud import user as user_crud
from app.schemas.magic_link import MagicLinkCreate, MagicLinkResponse, MagicLinkSend
from app.services.email_service import email_service
from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.auth import UserAuth

router = APIRouter()


@router.post("/auth/magic/send", response_model=MagicLinkResponse)
def send_magic_link(
    magic_link_data: MagicLinkSend,
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Send a magic link for passwordless authentication.
    
    This endpoint generates a JWT-based magic link token, stores it in the database,
    and sends an email to the user with the magic link.
    """
    try:
        # Create magic link
        jwt_token, magic_link_response = crud_magic_link.create_magic_link(
            db=db,
            magic_link_data=MagicLinkCreate(
                email=magic_link_data.email,
                purpose=magic_link_data.purpose,
                workspace_id=magic_link_data.workspace_id
            )
        )
        
        # Build magic link URL
        backend_base = settings.BACKEND_URL.rstrip('/')
        magic_link_url = f"{backend_base}/auth/magic/verify?token={jwt_token}"
        
        # Send email
        if magic_link_data.purpose == "login":
            email_service.send_magic_link_login_email(
                to_email=magic_link_data.email,
                magic_link=magic_link_url
            )
        elif magic_link_data.purpose == "signup":
            email_service.send_magic_link_signup_email(
                to_email=magic_link_data.email,
                magic_link=magic_link_url
            )
        else:
            email_service.send_magic_link_generic_email(
                to_email=magic_link_data.email,
                magic_link=magic_link_url,
                purpose=magic_link_data.purpose
            )
        
        return magic_link_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send magic link: {str(e)}")


@router.get("/auth/magic/verify")
def verify_magic_link(
    token: str = Query(..., description="Magic link JWT token"),
    redirect_base_url: Optional[str] = Query(None, description="Frontend base URL for redirect"),
    redirect_path: Optional[str] = Query("/auth-callback", description="Path on frontend after login"),
    cookie_domain: Optional[str] = Query(None, description="Cookie domain for cross-domain auth"),
    db: Session = Depends(get_db),
):
    """
    Verify magic link token, authenticate user, and redirect to frontend.
    
    This endpoint:
    1. Validates the JWT token
    2. Checks database for token validity
    3. Marks token as used
    4. Creates/activates user if needed
    5. Issues session JWT
    6. Sets HttpOnly cookie
    7. Redirects to frontend
    """
    try:
        # Verify magic link token
        magic_link_info = crud_magic_link.verify_magic_link_token(db=db, token=token)
        
        # Mark token as used and get user details
        usage_result = crud_magic_link.mark_magic_link_as_used(db=db, token=token)
        
        # Get user details
        user = user_crud.get_user_by_email(db, magic_link_info.email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found after magic link verification")
        
        # Generate session JWT
        user_auth = UserAuth(
            user_id=user.user_id,
            email=user.email,
            name=user.name,
            picture=user.picture,
            role=user.role,
            tenant_id=user.tenant_id
        )
        
        access_token = create_access_token(data=user_auth.dict())
        
        # Build redirect URL with token + workspace context for FE auth-callback
        base_url = redirect_base_url if redirect_base_url else settings.FRONTEND_URL
        path = redirect_path or "/auth-callback"
        query_params = []
        query_params.append(f"token={access_token}")
        if magic_link_info.workspace_id:
            query_params.append(f"workspace_id={magic_link_info.workspace_id}")
        final_query = ("?" + "&".join(query_params)) if query_params else ""
        final_url = f"{base_url.rstrip('/')}{('/' + path.lstrip('/')) if path else '/auth-callback'}{final_query}"
        
        # Set HttpOnly cookie and redirect
        response = RedirectResponse(url=final_url, status_code=302)
        
        # Determine cookie settings based on environment
        is_local = base_url.startswith("http://localhost") or base_url.startswith("http://127.0.0.1")
        
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=not is_local,
            samesite="none" if not is_local else "lax",
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path="/",
            domain=cookie_domain if cookie_domain else None,
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Magic link verification failed: {str(e)}")


@router.post("/auth/magic/authenticate")
def authenticate_with_magic_link(
    token: str = Query(..., description="Magic link JWT token"),
    cookie_domain: Optional[str] = Query(None, description="Cookie domain for cross-domain auth"),
    db: Session = Depends(get_db),
):
    """
    Authenticate user with magic link and return JWT token (API endpoint).
    
    This endpoint is for programmatic authentication where you need the JWT token
    in the response body rather than a redirect.
    """
    try:
        # Verify magic link token
        magic_link_info = crud_magic_link.verify_magic_link_token(db=db, token=token)
        
        # Mark token as used and get user details
        usage_result = crud_magic_link.mark_magic_link_as_used(db=db, token=token)
        
        # Get user details
        user = user_crud.get_user_by_email(db, magic_link_info.email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found after magic link verification")
        
        # Generate session JWT
        user_auth = UserAuth(
            user_id=user.user_id,
            email=user.email,
            name=user.name,
            picture=user.picture,
            role=user.role,
            tenant_id=user.tenant_id
        )
        
        access_token = create_access_token(data=user_auth.dict())
        
        # Create response with JWT token
        response_data = {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_auth.dict(),
            "workspace_id": magic_link_info.workspace_id
        }
        
        response = JSONResponse(content=response_data)
        
        # Set HttpOnly cookie for frontend proxy compatibility
        is_local = settings.FRONTEND_URL.startswith("http://localhost") or settings.FRONTEND_URL.startswith("http://127.0.0.1")
        
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=not is_local,
            samesite="none" if not is_local else "lax",
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path="/",
            domain=cookie_domain if cookie_domain else None,
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Magic link authentication failed: {str(e)}")


@router.get("/auth/magic/status/{token}")
def check_magic_link_status(
    token: str,
    db: Session = Depends(get_db),
):
    """
    Check the status of a magic link token without consuming it.
    
    This endpoint is useful for frontend validation before attempting to use the token.
    """
    try:
        magic_link_info = crud_magic_link.verify_magic_link_token(db=db, token=token)
        return {
            "is_valid": True,
            "email": magic_link_info.email,
            "purpose": magic_link_info.purpose,
            "workspace_id": magic_link_info.workspace_id,
            "expires_at": magic_link_info.expires_at
        }
    except HTTPException as e:
        return {
            "is_valid": False,
            "error": e.detail,
            "status_code": e.status_code
        }


@router.delete("/auth/magic/cleanup")
def cleanup_expired_magic_links(
    db: Session = Depends(get_db),
):
    """
    Clean up expired magic links from the database.
    
    This endpoint can be called periodically to maintain database hygiene.
    """
    try:
        cleaned_count = crud_magic_link.cleanup_expired_magic_links(db=db)
        return {
            "message": f"Cleaned up {cleaned_count} expired magic links",
            "cleaned_count": cleaned_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

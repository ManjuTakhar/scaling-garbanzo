from fastapi import APIRouter, Depends, HTTPException, Query, Header, Request
from fastapi.responses import RedirectResponse
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.crud import user as user_crud
from app.crud import workspace_invitation as crud_invitation
from app.schemas.workspace_invitation import (
    WorkspaceInvitationCreate, 
    WorkspaceInvitationResponse, 
    WorkspaceInvitationAccept, 
    WorkspaceInvitationListResponse,
    MagicLinkResponse,
    WorkspaceInvitationLinkResponse
)
from app.services.email_service import email_service
from app.core.config import settings

router = APIRouter()


@router.post("/workspaces/{workspace_id}/invite", response_model=WorkspaceInvitationResponse)
def send_workspace_invitation(
    workspace_id: str,
    invitation_data: WorkspaceInvitationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...),
    redirect_base_url: Optional[str] = Query(None, description="Override the frontend base URL for magic link (e.g., http://localhost:3000)"),
    redirect_path: Optional[str] = Query("/auth-callback", description="Path on the frontend to open after clicking the invite"),
    cookie_domain: Optional[str] = Query(None, description="Frontend host for cookie domain (e.g., app.example.com)"),
    next_path: Optional[str] = Query("/dashboard", description="Target route after FE callback (e.g., /dashboard)"),
    proxy_prefix: Optional[str] = Query(None, description="Optional proxy prefix when FE forwards to BE (e.g., /api/v1)"),
    request: Request = None,
):
    """Send a workspace invitation via email with magic link. Auth required."""
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    from app.crud import workspace as crud_workspace
    db_workspace = crud_workspace.get_workspace_by_id(db, workspace_id)
    if not db_workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    is_creator = (db_workspace.created_by == user.user_id)
    current_user_member = crud_workspace.get_workspace_member_by_user_id(db, workspace_id, user.user_id)
    is_admin = (current_user_member and current_user_member.role == "Admin")
    if not (is_creator or is_admin):
        raise HTTPException(status_code=403, detail="Not authorized to send invitations to this workspace")

    # Create invitation with actual user ID
    invitation_result = crud_invitation.create_workspace_invitation_with_token(
        db=db,
        workspace_id=workspace_id,
        invitation_data=invitation_data,
        invited_by=user.user_id
    )

    # Build magic link to backend verify endpoint; include FE redirect and cookie domain
    frontend_base = (redirect_base_url or settings.FRONTEND_URL).rstrip('/')
    path = redirect_path or "/dashboard"
    backend_base = settings.BACKEND_URL.rstrip('/')

    # If testing locally or a proxy prefix is provided, build link to FE origin + proxy
    use_frontend_proxy = False
    if redirect_base_url:
        lower_base = redirect_base_url.lower()
        if "localhost" in lower_base or "127.0.0.1" in lower_base:
            use_frontend_proxy = True
    if cookie_domain and cookie_domain.lower() in ("localhost", "127.0.0.1"):
        use_frontend_proxy = True
    if proxy_prefix:
        use_frontend_proxy = True

    if use_frontend_proxy:
        prefix = proxy_prefix or "/api/v1"
        magic_link = (
            f"{frontend_base}{prefix}/auth/verify-magic-link?token={invitation_result['magic_token']}"
            f"&redirect_base_url={frontend_base}"
            f"&redirect_path={path}"
            f"&next_path={next_path}"
            f"{f'&cookie_domain={cookie_domain}' if cookie_domain else ''}"
            f"&invite_id={invitation_result['invitation'].invitation_id}"
            f"&workspace_id={workspace_id}"
            f"&role_to_assign={invitation_data.role}"
            f"&action=accept_invite"
        )
    else:
        magic_link = (
            f"{backend_base}/auth/verify-magic-link?token={invitation_result['magic_token']}"
            f"&redirect_base_url={frontend_base}"
            f"&redirect_path={path}"
            f"&next_path={next_path}"
            f"{f'&cookie_domain={cookie_domain}' if cookie_domain else ''}"
            f"&invite_id={invitation_result['invitation'].invitation_id}"
            f"&workspace_id={workspace_id}"
            f"&role_to_assign={invitation_data.role}"
            f"&action=accept_invite"
        )
    email_service.send_workspace_invitation_email(
        to_email=invitation_data.email,
        workspace_name=db_workspace.name,
        inviter_name=user.name,
        magic_link=magic_link,
        role=invitation_data.role
    )

    return invitation_result['invitation']


@router.post("/workspaces/{workspace_id}/invite-link", response_model=WorkspaceInvitationLinkResponse)
def generate_workspace_invite_link(
    workspace_id: str,
    invitation_data: WorkspaceInvitationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...),
    redirect_base_url: Optional[str] = Query(None, description="Override the frontend base URL for magic link (e.g., http://localhost:3000)"),
    redirect_path: Optional[str] = Query("/auth-callback", description="Path on the frontend to open after clicking the invite"),
    cookie_domain: Optional[str] = Query(None, description="Frontend host for cookie domain (e.g., app.example.com)"),
    next_path: Optional[str] = Query("/dashboard", description="Target route after FE callback (e.g., /dashboard)"),
    proxy_prefix: Optional[str] = Query(None, description="Optional proxy prefix when FE forwards to BE (e.g., /api/v1)"),
    request: Request = None,
):
    """Generate a workspace invitation link without sending email. Auth required."""
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    from app.crud import workspace as crud_workspace
    db_workspace = crud_workspace.get_workspace_by_id(db, workspace_id)
    if not db_workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    is_creator = (db_workspace.created_by == user.user_id)
    current_user_member = crud_workspace.get_workspace_member_by_user_id(db, workspace_id, user.user_id)
    is_admin = (current_user_member and current_user_member.role == "Admin")
    if not (is_creator or is_admin):
        raise HTTPException(status_code=403, detail="Not authorized to generate invitation links for this workspace")

    # Create invitation with actual user ID
    invitation_result = crud_invitation.create_workspace_invitation_with_token(
        db=db,
        workspace_id=workspace_id,
        invitation_data=invitation_data,
        invited_by=user.user_id
    )

    # Build magic link to backend verify endpoint; include FE redirect and cookie domain
    frontend_base = (redirect_base_url or settings.FRONTEND_URL).rstrip('/')
    path = redirect_path or "/dashboard"
    backend_base = settings.BACKEND_URL.rstrip('/')

    # If testing locally or a proxy prefix is provided, build link to FE origin + proxy
    use_frontend_proxy = False
    if redirect_base_url:
        lower_base = redirect_base_url.lower()
        if "localhost" in lower_base or "127.0.0.1" in lower_base:
            use_frontend_proxy = True
    if cookie_domain and cookie_domain.lower() in ("localhost", "127.0.0.1"):
        use_frontend_proxy = True
    if proxy_prefix:
        use_frontend_proxy = True

    if use_frontend_proxy:
        prefix = proxy_prefix or "/api/v1"
        magic_link = (
            f"{frontend_base}{prefix}/auth/verify-magic-link?token={invitation_result['magic_token']}"
            f"&redirect_base_url={frontend_base}"
            f"&redirect_path={path}"
            f"&next_path={next_path}"
            f"{f'&cookie_domain={cookie_domain}' if cookie_domain else ''}"
            f"&invite_id={invitation_result['invitation'].invitation_id}"
            f"&workspace_id={workspace_id}"
            f"&role_to_assign={invitation_data.role}"
            f"&action=accept_invite"
        )
    else:
        magic_link = (
            f"{backend_base}/auth/verify-magic-link?token={invitation_result['magic_token']}"
            f"&redirect_base_url={frontend_base}"
            f"&redirect_path={path}"
            f"&next_path={next_path}"
            f"{f'&cookie_domain={cookie_domain}' if cookie_domain else ''}"
            f"&invite_id={invitation_result['invitation'].invitation_id}"
            f"&workspace_id={workspace_id}"
            f"&role_to_assign={invitation_data.role}"
            f"&action=accept_invite"
        )

    return WorkspaceInvitationLinkResponse(
        invitation_id=invitation_result['invitation'].invitation_id,
        workspace_id=workspace_id,
        email=invitation_data.email,
        role=invitation_data.role,
        magic_link=magic_link,
        expires_at=invitation_result['invitation'].expires_at,
        created_at=invitation_result['invitation'].created_at
    )


@router.get("/workspaces/{workspace_id}/invitations", response_model=List[WorkspaceInvitationResponse])
def list_workspace_invitations(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...),
):
    """List all pending invitations for a workspace. Only creator/admins can view."""
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return crud_invitation.list_workspace_invitations(
        db=db,
        workspace_id=workspace_id,
        user_id=user.user_id
    )


@router.delete("/workspaces/invitations/{invitation_id}")
def cancel_workspace_invitation(
    invitation_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...),
):
    """Cancel a workspace invitation. Only creator/admins can cancel."""
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return crud_invitation.cancel_workspace_invitation(
        db=db,
        invitation_id=invitation_id,
        user_id=user.user_id
    )


@router.get("/invitations/validate/{magic_token}", response_model=MagicLinkResponse)
def validate_invitation_link(
    magic_token: str,
    db: Session = Depends(get_db),
):
    """Validate a magic link token and return invitation details. No auth required."""
    return crud_invitation.validate_magic_link(db=db, magic_token=magic_token)


@router.post("/invitations/accept")
def accept_workspace_invitation(
    invitation_data: WorkspaceInvitationAccept,
    db: Session = Depends(get_db),
):
    """Accept a workspace invitation using magic link. No auth required."""
    return crud_invitation.accept_workspace_invitation(db=db, invitation_data=invitation_data)


# Additional endpoint for magic link authentication flow
@router.post("/auth/magic-link")
def magic_link_auth(
    magic_token: str,
    cookie_domain: Optional[str] = Query(None, description="Override cookie domain (set to frontend domain when using a proxy)"),
    db: Session = Depends(get_db),
):
    """Authenticate user via magic link and return JWT token. No auth required."""
    # Validate the magic link first
    invitation_info = crud_invitation.validate_magic_link(db=db, magic_token=magic_token)
    
    # Find or create user
    from app.crud import user as user_crud
    user = user_crud.get_user_by_email(db, invitation_info.email)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please accept the invitation first.")
    
    # Generate JWT token for the user
    from app.core.security import create_access_token
    from app.schemas.auth import UserAuth
    
    user_auth = UserAuth(
        user_id=user.user_id,
        email=user.email,
        name=user.name,
        picture=user.picture,
        role=user.role,
        tenant_id=user.tenant_id
    )
    
    access_token = create_access_token(data=user_auth.dict())
    
    # Set HttpOnly cookie for FE proxy-based auth
    response = JSONResponse(content={
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_auth.dict(),
        "workspace_id": invitation_info.workspace_id,
        "workspace_name": invitation_info.workspace_name
    })
    # Heuristic: mark secure=False for localhost
    from app.core.config import settings
    base_url = settings.FRONTEND_URL
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


@router.get("/auth/verify-magic-link")
def verify_magic_link(
    token: str = Query(..., description="Magic link token"),
    redirect_base_url: Optional[str] = Query(None, description="Override the frontend base URL for redirect"),
    redirect_path: Optional[str] = Query("/auth-callback", description="Path on the frontend after login"),
    next_path: Optional[str] = Query("/dashboard", description="Where the FE should route after callback"),
    cookie_domain: Optional[str] = Query(None, description="Override cookie domain (set to frontend domain when using a proxy)"),
    db: Session = Depends(get_db),
):
    """Verify magic link, accept invite, set cookie, and redirect to frontend."""
    # Validate token
    invitation_info = crud_invitation.validate_magic_link(db=db, magic_token=token)

    # Ensure membership/user by accepting the invitation (idempotent behavior ensured by validate before)
    try:
        crud_invitation.accept_workspace_invitation(
            db=db,
            invitation_data=WorkspaceInvitationAccept(magic_token=token)
        )
    except HTTPException as e:
        # If already accepted, proceed; otherwise re-raise
        if e.status_code != 400 or "already been accepted" not in str(e.detail):
            raise

    # Issue JWT for the user - fetch fresh user data to ensure workspace_id is updated
    from app.crud import user as user_crud
    user = user_crud.get_user_by_email(db, invitation_info.email)
    if not user:
        # This should be created during accept; guard just in case
        raise HTTPException(status_code=404, detail="User not found after accepting invitation")
    
    # Ensure the user's workspace_id is set to the invited workspace
    # Use CRUD setter to avoid mutating Pydantic models
    if user.workspace_id != invitation_info.workspace_id:
        from app.crud import user as user_crud
        user_crud.set_user_workspace_id(db, user.user_id, invitation_info.workspace_id)

    from app.core.security import create_access_token
    from app.schemas.auth import UserAuth

    user_auth = UserAuth(
        user_id=user.user_id,
        email=user.email,
        name=user.name,
        picture=user.picture,
        role=user.role,
        tenant_id=user.tenant_id,
    )
    access_token = create_access_token(data=user_auth.dict())

    # Build redirect URL with access_token and next
    base_url = redirect_base_url if redirect_base_url else settings.FRONTEND_URL
    path = redirect_path or "/auth-callback"
    query_parts = [f"access_token={access_token}"]
    if invitation_info.workspace_id:
        query_parts.append(f"workspace_id={invitation_info.workspace_id}")
    if next_path:
        query_parts.append(f"next={next_path}")
    query_str = "?" + "&".join(query_parts)
    final_url = f"{base_url.rstrip('/')}{('/' + path.lstrip('/')) if path else '/auth-callback'}{query_str}"

    # Set HttpOnly cookie and redirect
    response = RedirectResponse(url=final_url, status_code=302)
    # Heuristic: mark secure=False for localhost
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


@router.get("/test-email-config")
def test_email_config():
    """Test endpoint to check email configuration. No auth required."""
    from app.core.config import settings
    
    config_status = {
        "smtp_server": settings.SMTP_SERVER,
        "smtp_port": settings.SMTP_PORT,
        "username_set": bool(settings.SMTP_USERNAME),
        "password_set": bool(settings.SMTP_PASSWORD),
        "from_email": settings.FROM_EMAIL,
        "username_preview": settings.SMTP_USERNAME[:3] + "***" if settings.SMTP_USERNAME else "Not set"
    }
    
    return {
        "message": "Email configuration status",
        "config": config_status,
        "is_configured": bool(settings.SMTP_USERNAME and settings.SMTP_PASSWORD)
    }

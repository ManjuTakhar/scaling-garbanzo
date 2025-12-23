from fastapi import Depends, HTTPException, Request
from jose import jwt, JWTError
from app.auth.token_decoder import AuthJSDecoder
from app.core.config import settings
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.crud import user as user_crud
from app.models.workspace import WorkspaceMember

async def get_current_user(request: Request):
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    token = authorization.split(" ")[1]
    client_mode = request.headers.get("client-mode")

    # Always treat Authorization as NextAuth JWE (align with issues-core)
    token_decoder = AuthJSDecoder(settings.SECRET_KEY, client_mode == "prod")
    user_details = token_decoder.decode_jwe(token)
    if not user_details:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user_details

    # Note: Cookie fallback kept below for magic-link routes if needed
    # (Unreachable due to return above; enable only if you intend to support both flows here.)

async def get_current_user_with_workspace(request: Request, db: Session = Depends(get_db)):
    """Get current user and their workspace context for proper data isolation."""
    current_user = await get_current_user(request)
    
    # Get user from database to access tenant_id
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    # Get user's workspace membership
    workspace_membership = db.query(WorkspaceMember).filter(
        WorkspaceMember.user_id == user.user_id
    ).first()
    
    workspace_id = workspace_membership.workspace_id if workspace_membership else None
    
    return {
        "user": user,
        "workspace_id": workspace_id,
        "tenant_id": user.tenant_id,
        "current_user": current_user
    }

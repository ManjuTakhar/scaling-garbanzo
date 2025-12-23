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
    print(f"authorization ***************************************: {authorization}")
    if authorization:
        token = authorization.split(" ")[1]
        print(f"token: {token}")
        # Detect token type: JWE has 5 segments (4 dots), JWT has 3 segments (2 dots)
        segment_count = token.count(".")
        if segment_count == 4:
            print(f"segment_count: {segment_count}")
            client_mode = request.headers.get("client-mode")
            print(f"client_mode: {client_mode}")
            token_decoder = AuthJSDecoder(settings.SECRET_KEY, client_mode == "prod")
            user_details = token_decoder.decode_jwe(token)
            if not user_details:
                raise HTTPException(status_code=401, detail="Invalid token")
        else:
            # Standard JWT: decode directly
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                user_details = {
                    "email": payload.get("email") or payload.get("mail") or payload.get("preferred_username"),
                    "name": payload.get("name"),
                    "picture": payload.get("picture"),
                    "role": payload.get("role"),
                    "tenant_id": payload.get("tenant_id"),
                    "sub": payload.get("sub") or payload.get("user_id"),
                }
            except JWTError:
                raise HTTPException(status_code=401, detail="Invalid token")

        # If email not present, try to decode nested accessToken (JWT) to enrich details
        if not isinstance(user_details, dict):
            raise HTTPException(status_code=401, detail="Invalid token")
        try:
            if isinstance(user_details.get("accessToken"), str):
                nested_payload = jwt.decode(
                    user_details["accessToken"],
                    settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM],
                )
                # Merge selected fields from nested token
                enriched = dict(user_details)
                for key in ("name", "picture", "role", "tenant_id", "sub", "user_id"):
                    if key in nested_payload and not enriched.get(key):
                        enriched[key] = nested_payload.get(key)
                # Prefer an email-like field from nested token and mirror to both email and mail
                email_candidate = (
                    nested_payload.get("email")
                    or nested_payload.get("mail")
                    or nested_payload.get("preferred_username")
                )
                if email_candidate:
                    if not enriched.get("email"):
                        enriched["email"] = email_candidate
                    # mirror as 'mail' for compatibility if missing
                    if not enriched.get("mail"):
                        enriched["mail"] = email_candidate
                # Some tokens may use user_id rather than sub
                if not enriched.get("sub") and nested_payload.get("user_id"):
                    enriched["sub"] = nested_payload.get("user_id")
                user_details = enriched
        except JWTError:
            # Ignore enrichment failure; downstream may still work if cookie path sets email
            pass
        print(f"user_details: {user_details}")
        return user_details

    # Fallback: support HttpOnly cookie-based auth set by magic-link login
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        try:
            payload = jwt.decode(cookie_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            # Expect our magic-link JWT payload to include email, name, picture, tenant_id
            email = payload.get("email")
            if not email:
                raise HTTPException(status_code=401, detail="Invalid cookie token")
            user_details = {
                "email": email,
                "name": payload.get("name"),
                "picture": payload.get("picture"),
                "sub": payload.get("user_id"),
                "tenant_id": payload.get("tenant_id"),
            }
            return user_details
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid cookie token")

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

from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException
from app.models.magic_link import MagicLink
from app.models.user import User
from app.schemas.magic_link import MagicLinkCreate, MagicLinkResponse, MagicLinkVerify
from app.core.security import create_access_token, verify_token
from app.utils.utils import generate_custom_id
from datetime import datetime, timedelta, timezone
import secrets
import hashlib
import jwt
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def generate_magic_link_token(email: str, purpose: str = "login", workspace_id: Optional[str] = None, extra_claims: Optional[dict] = None) -> tuple[str, str]:
    """
    Generate a JWT-based magic link token and return both the token and its hash.
    
    Args:
        email: User's email address
        purpose: Purpose of the magic link ("login", "signup", "invite")
        workspace_id: Optional workspace context
        
    Returns:
        tuple: (jwt_token, token_hash)
    """
    # Generate a unique token ID
    token_id = f"ML-{generate_custom_id(email)}"
    
    # Create JWT payload
    payload = {
        "token_id": token_id,
        "email": email,
        "purpose": purpose,
        "workspace_id": workspace_id,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)  # 30 minutes expiry
    }
    if extra_claims:
        payload.update(extra_claims)
    
    # Generate JWT token
    jwt_token = jwt.encode(payload, "magic_link_secret", algorithm="HS256")
    
    # Create hash for database storage
    token_hash = hashlib.sha256(jwt_token.encode()).hexdigest()
    
    return jwt_token, token_hash


def create_magic_link(
    db: Session, 
    magic_link_data: MagicLinkCreate,
    extra_claims: Optional[dict] = None
) -> tuple[str, MagicLinkResponse]:
    """
    Create a new magic link and store it in the database.
    
    Args:
        db: Database session
        magic_link_data: Magic link creation data
        
    Returns:
        tuple: (jwt_token, magic_link_response)
    """
    # Check if user exists (for login purpose)
    if magic_link_data.purpose == "login":
        user = db.query(User).filter(User.email == magic_link_data.email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    
    # Generate token and hash
    jwt_token, token_hash = generate_magic_link_token(
        email=magic_link_data.email,
        purpose=magic_link_data.purpose,
        workspace_id=magic_link_data.workspace_id,
        extra_claims=extra_claims
    )
    
    # Create token ID with timestamp to ensure uniqueness
    timestamp = int(datetime.now(timezone.utc).timestamp())
    token_id = f"ML-{generate_custom_id(magic_link_data.email)}-{timestamp}"
    
    # Always create new magic link (allow multiple invitations)
    db_magic_link = MagicLink(
        token_id=token_id,
        email=magic_link_data.email,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        purpose=magic_link_data.purpose,
        workspace_id=magic_link_data.workspace_id
    )
    
    db.add(db_magic_link)
    db.commit()
    db.refresh(db_magic_link)
    
    magic_link_response = MagicLinkResponse(
        token_id=db_magic_link.token_id,
        email=db_magic_link.email,
        expires_at=int(db_magic_link.expires_at.timestamp()),
        purpose=db_magic_link.purpose,
        workspace_id=db_magic_link.workspace_id
    )
    
    return jwt_token, magic_link_response


def verify_magic_link_token(db: Session, token: str) -> MagicLinkResponse:
    """
    Verify a magic link token and return its details.
    
    Args:
        db: Database session
        token: JWT token to verify
        
    Returns:
        MagicLinkResponse: Token details if valid
        
    Raises:
        HTTPException: If token is invalid, expired, or already used
    """
    try:
        # Decode JWT token
        payload = jwt.decode(token, "magic_link_secret", algorithms=["HS256"])
        
        # Extract token details
        token_id = payload.get("token_id")
        email = payload.get("email")
        purpose = payload.get("purpose")
        workspace_id = payload.get("workspace_id")
        
        if not all([token_id, email, purpose]):
            raise HTTPException(status_code=400, detail="Invalid token format")
        
        # Create hash to find in database
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Find token in database
        magic_link = db.query(MagicLink).filter(
            and_(
                MagicLink.token_id == token_id,
                MagicLink.token_hash == token_hash
            )
        ).first()
        
        if not magic_link:
            raise HTTPException(status_code=404, detail="Invalid magic link token")
        
        # Check if token is already used
        if magic_link.is_used:
            raise HTTPException(status_code=400, detail="Magic link has already been used")
        
        # Check if token is expired
        if magic_link.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Magic link has expired")
        
        return MagicLinkResponse(
            token_id=magic_link.token_id,
            email=magic_link.email,
            expires_at=int(magic_link.expires_at.timestamp()),
            purpose=magic_link.purpose,
            workspace_id=magic_link.workspace_id
        )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Magic link has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid magic link token")
    except Exception as e:
        logger.error(f"Error verifying magic link token: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


def mark_magic_link_as_used(db: Session, token: str) -> dict:
    """
    Mark a magic link token as used after successful authentication.
    
    Args:
        db: Database session
        token: JWT token to mark as used
        
    Returns:
        dict: Success message and user details
    """
    try:
        # Decode JWT token to get token_id
        payload = jwt.decode(token, "magic_link_secret", algorithms=["HS256"])
        token_id = payload.get("token_id")
        email = payload.get("email")
        
        if not token_id:
            raise HTTPException(status_code=400, detail="Invalid token format")
        
        # Find and mark token as used
        magic_link = db.query(MagicLink).filter(MagicLink.token_id == token_id).first()
        
        if not magic_link:
            raise HTTPException(status_code=404, detail="Magic link not found")
        
        if magic_link.is_used:
            raise HTTPException(status_code=400, detail="Magic link already used")
        
        # Mark as used
        magic_link.is_used = True
        magic_link.used_at = datetime.now(timezone.utc)
        db.commit()
        
        # Get or create user
        user = db.query(User).filter(User.email == email).first()
        
        if not user and magic_link.purpose == "signup":
            # Create new user for signup
            from app.schemas.user import UserCreate
            from app.crud.user import create_user
            
            # Derive tenant from workspace if present, otherwise raise for explicit handling
            tenant_id_for_user = None
            if magic_link.workspace_id:
                from app.crud.workspace import get_workspace_by_id
                ws = get_workspace_by_id(db, magic_link.workspace_id)
                if ws:
                    tenant_id_for_user = ws.tenant_id
            if not tenant_id_for_user:
                raise HTTPException(status_code=400, detail="Cannot determine tenant for signup; workspace required")

            user_data = UserCreate(
                email=email,
                name=email.split('@')[0],  # Use email prefix as default name
                picture=None,
                role="Engineer",
                tenant_id=tenant_id_for_user
            )
            user = create_user(db, user_data)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "message": "Magic link used successfully",
            "user_id": user.user_id,
            "email": user.email,
            "workspace_id": magic_link.workspace_id
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Magic link has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid magic link token")
    except Exception as e:
        logger.error(f"Error marking magic link as used: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


def cleanup_expired_magic_links(db: Session) -> int:
    """
    Clean up expired magic links from the database.
    
    Args:
        db: Database session
        
    Returns:
        int: Number of expired links removed
    """
    expired_count = db.query(MagicLink).filter(
        MagicLink.expires_at < datetime.now(timezone.utc)
    ).count()
    
    db.query(MagicLink).filter(
        MagicLink.expires_at < datetime.now(timezone.utc)
    ).delete()
    
    db.commit()
    
    logger.info(f"Cleaned up {expired_count} expired magic links")
    return expired_count

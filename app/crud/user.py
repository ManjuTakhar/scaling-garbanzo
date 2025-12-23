from sqlalchemy.orm import Session
import uuid
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import UserAuth
from datetime import datetime
from fastapi import HTTPException
from typing import Optional, List
from app.models.workspace import WorkspaceMember


def create_user(db: Session, user: UserCreate) -> UserResponse:
    """Create a new user in the database."""
    db_user = User(
        name=user.name,
        email=user.email,
        role=user.role,
        picture=user.picture,
        tenant_id=user.tenant_id,
        workspace_id=user.workspace_id
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return UserResponse(
        user_id=db_user.user_id,
        name=db_user.name,
        email=db_user.email,
        role=db_user.role,
        picture=db_user.picture,
        tenant_id=db_user.tenant_id,
        workspace_id=db_user.workspace_id,
        created_at=int(db_user.created_at.timestamp()),
        last_updated=int(db_user.last_updated.timestamp()) if db_user.last_updated else None
    )

def get_all_users(db: Session, team_id: Optional[str] = None, workspace_id: Optional[str] = None) -> List[dict]:
    """Fetch all users, optionally filtered by team membership, tenant, or workspace."""
    query = db.query(User)

    if team_id:
        query = (
            query.join(TeamMember, TeamMember.user_id == User.user_id)
                 .filter(TeamMember.team_id == team_id)
        )
    
    # If workspace_id provided, filter users who are members of that workspace
    if workspace_id:
        query = (
            query.join(WorkspaceMember, WorkspaceMember.user_id == User.user_id)
                 .filter(WorkspaceMember.workspace_id == workspace_id)
        )

    users = query.all()
    return [UserResponse(
        user_id=user.user_id,
        name=user.name,
        email=user.email,
        role=user.role,
        picture=user.picture,
        tenant_id=user.tenant_id,
        workspace_id=user.workspace_id,
        created_at=int(user.created_at.timestamp()),
        last_updated=int(user.last_updated.timestamp()) if user.last_updated else None
    ) for user in users]

def get_user(db: Session, user_id: str) -> UserResponse:
    """Get a user by their user_id."""
    db_user = db.query(User).filter(User.user_id == user_id).first()
    return UserResponse(
        user_id=str(db_user.user_id),
        name=db_user.name,
        email=db_user.email,
        role=db_user.role,
        picture=db_user.picture,
        tenant_id=db_user.tenant_id,
        workspace_id=db_user.workspace_id,
        created_at=int(db_user.created_at.timestamp()),
        last_updated=int(db_user.last_updated.timestamp()) if db_user.last_updated else None
    )

def get_user_by_email(db: Session, email: str) -> UserResponse:
    """Get a user by their email address."""
    db_user = db.query(User).filter(User.email == email).first()
    print(f"db_user ***************************************: {db_user}")
    return UserResponse(
        user_id=str(db_user.user_id),
        name=db_user.name,
        email=db_user.email,
        role=db_user.role,
        picture=db_user.picture,
        tenant_id=db_user.tenant_id if db_user.tenant_id else "34",
        workspace_id=db_user.workspace_id if db_user.workspace_id else "34",
        created_at=int(db_user.created_at.timestamp()),
        last_updated=int(db_user.last_updated.timestamp()) if db_user.last_updated else None
    ) if db_user else None

def create_or_update_user(db: Session, user_data: UserAuth):
    db_user = get_user_by_email(db, email=user_data.email)
    
    if db_user:
        # Update existing user
        for key, value in user_data.dict().items():
            setattr(db_user, key, value)
        db_user.last_login = int(datetime.utcnow().timestamp())
    else:
        # Create new user
        user_dict = user_data.dict()
        user_dict['role'] = "USER"  # Set default role
        user_dict['last_login'] = int(datetime.utcnow().timestamp())
        db_user = User(**user_dict)
        db.add(db_user)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: str) -> UserResponse:
    """Fetch a user by their user_id."""
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="User not found")

    return UserResponse(
        user_id=str(db_user.user_id),
        name=db_user.name,
        email=db_user.email,
        role=db_user.role,
        picture=db_user.picture,
        tenant_id=db_user.tenant_id,
        workspace_id=getattr(db_user, "workspace_id", None),
        created_at=int(db_user.created_at.timestamp()),
        last_updated=int(db_user.last_updated.timestamp()) if db_user.last_updated else None
    )

def set_user_workspace_id(db: Session, user_id: str, workspace_id: str) -> None:
    """Persist workspace_id on the user record."""
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        return
    db_user.workspace_id = workspace_id
    db.commit()
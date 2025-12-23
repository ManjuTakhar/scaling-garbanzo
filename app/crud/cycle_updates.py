from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.cycle_update import CycleUpdate
from app.models.user import User as UserModel


def _user_min(db: Session, user_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not user_id:
        return None
    row = db.query(
        UserModel.user_id, UserModel.name, UserModel.email, UserModel.picture
    ).filter(UserModel.user_id == user_id).first()
    if not row:
        return None
    return {
        "user_id": row.user_id,
        "name": row.name,
        "email": row.email,
        "picture": row.picture,
    }


def _to_dict(db: Session, cu: CycleUpdate) -> Dict[str, Any]:
    return {
        "id": cu.id,
        "cycle_id": cu.cycle_id,
        "content": cu.content,
        "created_by": _user_min(db, cu.created_by),
        "updated_by": _user_min(db, cu.updated_by),
        "created_at": int(cu.created_at.timestamp()) if cu.created_at else None,
        "updated_at": int(cu.updated_at.timestamp()) if cu.updated_at else None,
    }


def create_cycle_update(db: Session, cycle_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    created_by = update_data.get("created_by")
    # Validate user exists (minimal lookup)
    if not db.query(UserModel.user_id).filter(UserModel.user_id == created_by).first():
        raise HTTPException(status_code=404, detail="User not found")

    cu = CycleUpdate(
        cycle_id=cycle_id,
        content=update_data["content"],
        created_by=created_by,
        updated_by=created_by,
    )
    db.add(cu)
    db.commit()
    db.refresh(cu)
    return _to_dict(db, cu)


def get_cycle_updates(db: Session, cycle_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    rows = (
        db.query(CycleUpdate)
        .filter(CycleUpdate.cycle_id == cycle_id)
        .order_by(CycleUpdate.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [_to_dict(db, r) for r in rows]


def get_cycle_update(db: Session, update_id: str) -> Optional[Dict[str, Any]]:
    cu = db.query(CycleUpdate).filter(CycleUpdate.id == update_id).first()
    if not cu:
        return None
    return _to_dict(db, cu)


def update_cycle_update(db: Session, update_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    cu = db.query(CycleUpdate).filter(CycleUpdate.id == update_id).first()
    if not cu:
        raise HTTPException(status_code=404, detail="Cycle update not found")

    if "content" in update_data and update_data["content"] is not None:
        cu.content = update_data["content"]
    if "updated_by" in update_data and update_data["updated_by"]:
        cu.updated_by = update_data["updated_by"]

    db.commit()
    db.refresh(cu)
    return _to_dict(db, cu)


def delete_cycle_update(db: Session, cycle_id: str, update_id: str) -> bool:
    cu = db.query(CycleUpdate).filter(
        CycleUpdate.id == update_id, CycleUpdate.cycle_id == cycle_id
    ).first()
    if not cu:
        raise HTTPException(status_code=404, detail="Cycle update not found")
    db.delete(cu)
    db.commit()
    return True



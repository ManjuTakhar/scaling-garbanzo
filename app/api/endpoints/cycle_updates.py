from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.crud import cycle_updates as cycle_updates_crud
from app.schemas.cycle_updates import CycleUpdateCreate, CycleUpdateUpdate

router = APIRouter()

@router.post("/{cycle_id}/updates", response_model=dict)
def create_cycle_update(
    *, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user),
    cycle_id: str,
    update: CycleUpdateCreate
):
    """Create a new cycle update."""
    return cycle_updates_crud.create_cycle_update(db=db, cycle_id=cycle_id, update_data=update.dict())

@router.get("/{cycle_id}/updates", response_model=List[dict])
def list_cycle_updates(
    *, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    cycle_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Get all updates for a specific cycle."""
    return cycle_updates_crud.get_cycle_updates(db=db, cycle_id=cycle_id, skip=skip, limit=limit)

@router.get("/{cycle_id}/updates/{update_id}", response_model=dict)
def get_cycle_update(
    *, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user),
    cycle_id: str,
    update_id: str
):
    """Get a specific cycle update by ID."""
    update = cycle_updates_crud.get_cycle_update(db=db, update_id=update_id)
    if not update:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Cycle update not found")
    return update

@router.patch("/{cycle_id}/updates/{update_id}", response_model=dict)
def update_cycle_update(
    *, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user),
    cycle_id: str,
    update_id: str,
    update_data: CycleUpdateUpdate
):
    """Update a cycle update's content."""
    return cycle_updates_crud.update_cycle_update(db=db, update_id=update_id, update_data=update_data.dict(exclude_unset=True))

@router.delete("/{cycle_id}/updates/{update_id}")
def delete_cycle_update(
    *, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user),
    cycle_id: str,
    update_id: str
):
    """Delete a cycle update."""
    result = cycle_updates_crud.delete_cycle_update(db=db, cycle_id=cycle_id, update_id=update_id)
    return {"success": result, "message": "Cycle update deleted" if result else "Failed to delete"}


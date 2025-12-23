from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dto.dtos import EpicDTO
from app.crud import epics as epics_crud
from app.schemas.epics import EpicCreate, EpicUpdate

router = APIRouter()

@router.post("", response_model=EpicDTO)
def create_epic(*, db: Session = Depends(get_db), epic: EpicCreate):
    """Create a new epic."""
    return epics_crud.create_epic(db=db, epic_data=epic.dict())

@router.get("", response_model=List[EpicDTO])
def list_epics(
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """List all epics with pagination."""
    return epics_crud.list_epics(db=db, offset=offset, limit=limit)

@router.get("/{epic_id}", response_model=EpicDTO)
def get_epic(*, db: Session = Depends(get_db), epic_id: str):
    """Get a specific epic by ID."""
    epic = epics_crud.get_epic(db=db, epic_id=epic_id)
    if not epic:
        raise HTTPException(status_code=404, detail="Epic not found")
    return epic

@router.patch("/{epic_id}", response_model=EpicDTO)
def update_epic(
    *, db: Session = Depends(get_db), epic_id: str, epic_data: EpicUpdate
):
    """Update an epic."""
    return epics_crud.update_epic(db=db, epic_id=epic_id, epic_data=epic_data.dict(exclude_unset=True))

@router.delete("/{epic_id}")
def delete_epic(*, db: Session = Depends(get_db), epic_id: str):
    """Delete an epic."""
    epics_crud.delete_epic(db=db, epic_id=epic_id)
    return {"message": "Epic deleted successfully", "epic_id": epic_id}


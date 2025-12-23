from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.dto.dtos import CycleDTO
from app.crud import cycles as cycles_crud
from app.schemas.cycles import CycleCreate, CycleUpdate, StartCycleRequest, CompleteCycleRequest

router = APIRouter()

@router.post("", response_model=CycleDTO)
def create_cycle(*, db: Session = Depends(get_db), cycle: CycleCreate, current_user: dict = Depends(get_current_user)):
    """Create a new cycle."""
    return cycles_crud.create_cycle(db=db, cycle_data=cycle.dict())

@router.get("", response_model=List[CycleDTO])
def list_cycles(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    team_id: Optional[str] = Query(None, description="Filter by team ID"),
    status: Optional[str] = Query(None, description="Filter by status")
):
    """List all cycles."""
    return cycles_crud.get_cycles(db=db, team_id=team_id, status=status)

@router.get("/{cycle_id}", response_model=CycleDTO)
def get_cycle(*, db: Session = Depends(get_db), cycle_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific cycle by ID."""
    cycle = cycles_crud.get_cycle(db=db, cycle_id=cycle_id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    return cycle

@router.patch("/{cycle_id}", response_model=CycleDTO)
def update_cycle(
    *, db: Session = Depends(get_db), cycle_id: str, cycle_data: CycleUpdate, current_user: dict = Depends(get_current_user)
):
    """Update a cycle."""
    return cycles_crud.update_cycle(db=db, cycle_id=cycle_id, cycle_data=cycle_data.dict(exclude_unset=True))

@router.delete("/{cycle_id}")
def delete_cycle(*, db: Session = Depends(get_db), cycle_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a cycle."""
    cycles_crud.delete_cycle(db=db, cycle_id=cycle_id)
    return {"message": "Cycle deleted successfully", "cycle_id": cycle_id}


@router.post("/{cycle_id}/start", response_model=CycleDTO, summary="Start Cycle")
def start_cycle(*, db: Session = Depends(get_db), cycle_id: str, payload: StartCycleRequest, current_user: dict = Depends(get_current_user)):
    return cycles_crud.start_cycle(db=db, cycle_id=cycle_id, payload=payload)


@router.post("/{cycle_id}/complete", response_model=CycleDTO, summary="Complete Cycle")
def complete_cycle(*, db: Session = Depends(get_db), cycle_id: str, payload: CompleteCycleRequest, current_user: dict = Depends(get_current_user)):
    return cycles_crud.complete_cycle(db=db, cycle_id=cycle_id, payload=payload)


@router.get("/{cycle_id}/complete/info", summary="Get Complete Cycle Info")
def get_complete_cycle_info(*, db: Session = Depends(get_db), cycle_id: str, current_user: dict = Depends(get_current_user)):
    return cycles_crud.get_complete_cycle_info(db=db, cycle_id=cycle_id)


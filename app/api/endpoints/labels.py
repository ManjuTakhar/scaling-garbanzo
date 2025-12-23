from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dto.dtos import LabelDTO
from app.crud import labels as labels_crud

router = APIRouter()

@router.post("", response_model=LabelDTO)
def create_label(
    *, 
    db: Session = Depends(get_db), 
    name: str, 
    created_by: str,
    color: str = None,
    description: str = None
):
    """Create a new label."""
    return labels_crud.create_label(db=db, name=name, created_by=created_by, color=color, description=description)

@router.get("", response_model=List[LabelDTO])
def list_labels(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    issue_id: str = Query(None, description="Filter by issue ID")
):
    """List all labels."""
    return labels_crud.get_labels(db=db, issue_id=issue_id, skip=skip, limit=limit)

@router.post("/{label_id}/issues/{issue_id}", response_model=LabelDTO)
def add_label_to_issue(
    *, 
    db: Session = Depends(get_db), 
    label_id: str, 
    issue_id: str,
    created_by: str
):
    """Add a label to an issue."""
    # This will use add_label_to_issue with label name
    # TODO: Adapt based on actual label name vs ID
    raise NotImplementedError()

@router.delete("/{label_id}/issues/{issue_id}")
def remove_label_from_issue(
    *, 
    db: Session = Depends(get_db), 
    label_id: str, 
    issue_id: str
):
    """Remove a label from an issue."""
    result = labels_crud.remove_label_from_issue(db=db, issue_id=issue_id, label_id=label_id)
    return {"success": result, "message": "Label removed from issue" if result else "Label not found"}



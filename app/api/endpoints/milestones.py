from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.schemas.project import MilestoneCreate, Milestone, MilestoneUpdate, MilestoneResponse
from app.crud import milestone as crud_milestone
from app.db.session import SessionLocal
from app.db.session import get_db
from app.api.dependencies import get_current_user
from fastapi import Header
from app.crud import user as user_crud

router = APIRouter(
    tags=["milestones"]
)

@router.get("/projects/{project_id}/milestones", response_model=List[MilestoneResponse])
def list_milestones(project_id: str, 
                    db: Session = Depends(get_db),
                    current_user: dict = Depends(get_current_user),
                    authorization: str = Header(...)
                    ):
    """Get all milestones for a project"""
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return crud_milestone.get_project_milestones(db=db, project_id=project_id)

@router.post("/projects/{project_id}/milestones", response_model=MilestoneResponse)
def create_milestone(
    project_id: str,
    milestone: MilestoneCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Create a new milestone for a project"""
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return crud_milestone.create_milestone(db=db, project_id=project_id, milestone=milestone)

@router.patch("/milestones/{milestone_id}", response_model=MilestoneResponse)
async def update_milestone(
    milestone_id: str,
    milestone: MilestoneUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Update a milestone"""
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    db_milestone = crud_milestone.update_milestone(db=db, milestone_id=milestone_id, milestone=milestone)
    if not db_milestone:
        raise HTTPException(status_code=401, detail="Milestone not found")
    return db_milestone

@router.get("/milestones/{milestone_id}", response_model=MilestoneResponse)
def get_milestone(milestone_id: str, 
                  db: Session = Depends(get_db),
                  current_user: dict = Depends(get_current_user),
                  authorization: str = Header(...)
                  ):
    """Get a specific milestone by ID"""
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    db_milestone = crud_milestone.get_milestone(db, milestone_id=milestone_id)
    if not db_milestone:
        raise HTTPException(status_code=401, detail="Milestone not found")
    return db_milestone 
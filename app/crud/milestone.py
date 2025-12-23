from sqlalchemy.orm import Session
from app.models.project import Milestone
from app.schemas.project import MilestoneCreate, MilestoneUpdate, MilestoneResponse, UserDTO
from typing import List
from datetime import datetime

def get_project_milestones(db: Session, project_id: str) -> List[MilestoneResponse]:
    """Get all milestones for a project"""
    db_milestones = db.query(Milestone)\
        .filter(Milestone.project_id == project_id)\
        .order_by(Milestone.target_date.asc(), Milestone.last_updated.desc())\
        .all()
    return [MilestoneResponse(
        milestone_id=milestone.milestone_id,
        title=milestone.title,
        dri=UserDTO(
            user_id=milestone.created_by.user_id,
            email=milestone.created_by.email,
            name=milestone.created_by.name,
            role=milestone.created_by.role,
            picture=milestone.created_by.picture
        ) if milestone.created_by else None,
        target_date=int(milestone.target_date.timestamp()) if milestone.target_date else None,
        created_at=int(milestone.created_at.timestamp()),
        last_updated=int(milestone.last_updated.timestamp()) if milestone.last_updated else None,
        status=milestone.status,
        project_id=milestone.project_id
    ) for milestone in db_milestones]

def create_milestone(db: Session, project_id: str, milestone: MilestoneCreate) -> MilestoneResponse:
    """Create a new milestone"""
    db_milestone = Milestone(
        project_id=project_id,
        title=milestone.title,
        dri=milestone.dri,
        target_date=datetime.fromtimestamp(milestone.target_date) if milestone.target_date else None,
        status=milestone.status
    )
    db.add(db_milestone)
    db.commit()
    db.refresh(db_milestone)
    
    return MilestoneResponse(
        milestone_id=db_milestone.milestone_id,
        title=db_milestone.title,
        dri=UserDTO(
            user_id=db_milestone.created_by.user_id,
            email=db_milestone.created_by.email,
            name=db_milestone.created_by.name,
            role=db_milestone.created_by.role,
            picture=db_milestone.created_by.picture
        ) if db_milestone.created_by else None,
        target_date=int(db_milestone.target_date.timestamp()) if db_milestone.target_date else None,
        created_at=int(db_milestone.created_at.timestamp()),
        last_updated=int(db_milestone.last_updated.timestamp()),
        status=db_milestone.status,
        project_id=project_id
    )

def get_milestone(db: Session, milestone_id: str) -> MilestoneResponse:
    """Get a specific milestone by ID"""
    db_milestone = db.query(Milestone)\
        .filter(Milestone.milestone_id == milestone_id)\
        .first()
    
    return MilestoneResponse(
        milestone_id=db_milestone.milestone_id,
        title=db_milestone.title,
        dri=UserDTO(
            user_id=db_milestone.created_by.user_id,
            email=db_milestone.created_by.email,
            name=db_milestone.created_by.name,
            role=db_milestone.created_by.role,
            picture=db_milestone.created_by.picture
        ) if db_milestone.created_by else None,
        target_date=int(db_milestone.target_date.timestamp()) if db_milestone.target_date else None,
        status=db_milestone.status,
        project_id=db_milestone.project_id,
        created_at=int(db_milestone.created_at.timestamp()),
        last_updated=int(db_milestone.last_updated.timestamp()) if db_milestone.last_updated else None
    )

def update_milestone(db: Session, milestone_id: str, milestone: MilestoneUpdate) -> MilestoneResponse:
    """Update a milestone"""
    db_milestone = db.query(Milestone).filter(Milestone.milestone_id == milestone_id).first()
    if not db_milestone:
        return None
    
    update_data = milestone.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_milestone, field, value)
    db.commit()
    db.refresh(db_milestone)
    return MilestoneResponse(
        milestone_id=db_milestone.milestone_id,
        title=db_milestone.title,
        dri=UserDTO(
            user_id=db_milestone.created_by.user_id,
            email=db_milestone.created_by.email,
            name=db_milestone.created_by.name,
            role=db_milestone.created_by.role,
            picture=db_milestone.created_by.picture
        ) if db_milestone.created_by else None,
        target_date=int(db_milestone.target_date.timestamp()) if db_milestone.target_date else None,
        status=db_milestone.status,
        project_id=db_milestone.project_id,
        created_at=int(db_milestone.created_at.timestamp()),
        last_updated=int(db_milestone.last_updated.timestamp()) if db_milestone.last_updated else None
    )
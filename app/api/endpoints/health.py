from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.health import InitiativeHealthSummary, ProjectHealthSummary
from app.crud import health
from typing import List

router = APIRouter()

@router.get("/initiatives/{initiative_id}/health", response_model=InitiativeHealthSummary)
def get_initiative_health(
    initiative_id: str,
    db: Session = Depends(deps.get_db)
):
    return health.get_initiative_health_summary(db, initiative_id)


@router.get("/projects/{project_id}/health", response_model=ProjectHealthSummary)
def get_project_health(
    project_id: str,
    db: Session = Depends(deps.get_db)
):
    return health.get_project_health_summary(db, project_id) 
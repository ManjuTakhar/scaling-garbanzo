from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.project import Project, ProjectCreate, ProjectUpdate, ProjectResponse
from app.crud import project as crud_project
from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.crud import user as user_crud
router = APIRouter()

@router.post("/projects", response_model=ProjectResponse)
def create_project(
    project: ProjectCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Only authenticated users can create projects"""
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return crud_project.create_project(db=db, project=project)

@router.patch("/projects/{project_id}", response_model=ProjectResponse)
def update_project(project_id: str, project: ProjectUpdate, 
                   db: Session = Depends(get_db),
                   current_user: dict = Depends(get_current_user),
                   authorization: str = Header(...)):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return crud_project.update_project(db=db, project_id=project_id, project=project)

@router.get("/projects", response_model=List[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    dris: Optional[List[str]] = Query(None),
    teams: Optional[List[str]] = Query(None),
    status: Optional[str] = Query(None),
    workspace_id: Optional[str] = Query(None),
    authorization: str = Header(...)
):
    """Get all projects, optionally filtered by user IDs and team IDs."""
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return crud_project.get_projects(db=db, dris=dris, teams=teams, status=status, workspace_id=workspace_id)

@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str,
                db: Session = Depends(get_db),
                current_user: dict = Depends(get_current_user),
                authorization: str = Header(...)
                ):
    """Get a specific project by ID"""
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return crud_project.get_project(db, project_id=project_id)

@router.get("/initiatives/{initiative_id}/projects", response_model=List[ProjectResponse])
def get_initiative_projects(initiative_id: str, 
                            db: Session = Depends(get_db),
                            current_user: dict = Depends(get_current_user),
                            authorization: str = Header(...)):
    """Get all projects for a specific initiative"""
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return crud_project.get_initiative_projects(db, initiative_id=initiative_id)

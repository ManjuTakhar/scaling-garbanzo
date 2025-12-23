# app/api/endpoints/initiative_dependencies.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.crud import dependencies
from app.db.session import get_db  # Assuming you have a database connection setup
from app.schemas.dependencies import InitiativeDependencyCreate, InitiativeDependencyResponse, \
    ProjectDependencyCreate, ProjectDependencyResponse
from typing import List
from app.api.dependencies import get_current_user
from app.crud import user as user_crud
from fastapi import Header

router = APIRouter()

@router.post("/initiatives/{initiative_id}/dependencies", response_model=List[InitiativeDependencyResponse])
def create_initiative_dependency(
    initiative_id: str, 
    dependency: InitiativeDependencyCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...)
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return dependencies.create_initiative_dependency(db, initiative_id, dependency)

@router.get("/initiatives/{initiative_id}/dependencies", response_model=List[InitiativeDependencyResponse])
def get_initiative_dependencies(initiative_id: str, 
                                db: Session = Depends(get_db),
                                current_user: dict = Depends(get_current_user),
                                authorization: str = Header(...)):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return dependencies.get_initiative_dependencies(db, initiative_id)

@router.post("/projects/{project_id}/dependencies", response_model=List[ProjectDependencyResponse])
def create_project_dependency(
    project_id: str, 
    dependency: ProjectDependencyCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...)
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return dependencies.create_project_dependency(db, project_id, dependency)

@router.get("/projects/{project_id}/dependencies", response_model=List[ProjectDependencyResponse])
def get_project_dependencies(
    project_id: str, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...)
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return dependencies.get_project_dependencies(db, project_id)

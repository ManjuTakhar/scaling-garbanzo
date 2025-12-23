from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.resource import ResourceCreate, ResourceUpdate, ProjectResourceResponse, InitiativeResourceResponse
from app.crud import resources as crud_resources
from app.db.session import get_db
router = APIRouter()

@router.post("/projects/{project_id}/resources", response_model=ProjectResourceResponse)
def create_resource(
    project_id: str,
    resource: ResourceCreate,
    db: Session = Depends(get_db)
):
    return crud_resources.create_resource(db=db, project_id=project_id, resource=resource)

@router.get("/projects/{project_id}/resources", response_model=List[ProjectResourceResponse])
def list_project_resources(project_id: str, db: Session = Depends(get_db)):
    return crud_resources.get_project_resources(db=db, project_id=project_id)

@router.patch("/projects/{project_id}/resources/{resource_id}", response_model=ProjectResourceResponse)
def patch_project_resource(
    project_id: str,
    resource_id: str,   
    resource: ResourceUpdate,
    db: Session = Depends(get_db)
):
    return crud_resources.patch_project_resource(db=db, project_id=project_id, resource_id=resource_id, resource=resource)

@router.delete("/projects/resources/{resource_id}", response_model=ProjectResourceResponse)
def delete_resource(resource_id: str, db: Session = Depends(get_db)):
    crud_resources.delete_resource(db=db, resource_id=resource_id)
    return {"message": "Resource deleted successfully"} 

@router.post("/initiatives/{initiative_id}/resources", response_model=InitiativeResourceResponse)
def create_initiative_resource(
    initiative_id: str,
    resource: ResourceCreate,
    db: Session = Depends(get_db)
):
    return crud_resources.create_initiative_resource(db=db, initiative_id=initiative_id, resource=resource)

@router.get("/initiatives/{initiative_id}/resources", response_model=List[InitiativeResourceResponse])
def list_initiative_resources(initiative_id: str, db: Session = Depends(get_db)):
    return crud_resources.get_initiative_resources(db=db, initiative_id=initiative_id)

@router.patch("/initiatives/{initiative_id}/resources/{resource_id}", response_model=InitiativeResourceResponse)
def patch_initiative_resource(
    initiative_id: str,
    resource_id: str,
    resource: ResourceUpdate,
    db: Session = Depends(get_db)
):
    return crud_resources.patch_initiative_resource(db=db, initiative_id=initiative_id, resource_id=resource_id, resource=resource)

@router.delete("/initiatives/resources/{resource_id}", response_model=InitiativeResourceResponse)
def delete_initiative_resource(resource_id: str, db: Session = Depends(get_db)):
    crud_resources.delete_initiative_resource(db=db, resource_id=resource_id)
    return {"message": "Resource deleted successfully"} 
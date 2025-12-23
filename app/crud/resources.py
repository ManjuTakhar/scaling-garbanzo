from sqlalchemy.orm import Session
from app.models.resource import ProjectResource, InitiativeResource
from app.schemas.resource import ResourceCreate, ResourceUpdate, ProjectResourceResponse, InitiativeResourceResponse
from app.dto.dtos import UserDTO
from fastapi import HTTPException
from typing import List

def create_resource(db: Session, project_id: str, resource: ResourceCreate) -> ProjectResourceResponse:
    db_resource = ProjectResource(
        project_id=project_id,
        title=resource.title,
        url=resource.url,
        type=resource.type,
        created_by=resource.created_by,
        pinned=resource.pinned
    )
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return ProjectResourceResponse(
        resource_id=db_resource.resource_id,
        project_id=db_resource.project_id,
        title=db_resource.title,
        url=db_resource.url,
        type=db_resource.type,
        pinned=db_resource.pinned,
        created_by=UserDTO(
            user_id=db_resource.created_by,
            name=db_resource.created_by_user.name,
            role=db_resource.created_by_user.role,
            picture=db_resource.created_by_user.picture
        ),
        created_at=int(db_resource.created_at.timestamp()) if db_resource.created_at else None,
        last_updated=int(db_resource.last_updated.timestamp()) if db_resource.last_updated else None
    )

def get_project_resources(db: Session, project_id: str) -> List[ProjectResourceResponse]:
    db_resources = db.query(ProjectResource)\
        .filter(ProjectResource.project_id == project_id)\
        .order_by(ProjectResource.created_at.desc())\
        .all()
    return [ProjectResourceResponse(
        resource_id=resource.resource_id,
        project_id=resource.project_id,
        title=resource.title,
        url=resource.url,
        type=resource.type,
        pinned=resource.pinned,
        created_by=UserDTO( 
            user_id=resource.created_by,
            name=resource.created_by_user.name,
            role=resource.created_by_user.role,
            picture=resource.created_by_user.picture
        ),
        created_at=int(resource.created_at.timestamp()) if resource.created_at else None,
        last_updated=int(resource.last_updated.timestamp()) if resource.last_updated else None
    ) for resource in db_resources]

def patch_project_resource(db: Session, project_id: str, resource_id: str, resource: ResourceUpdate):
    db_resource = db.query(ProjectResource).filter(ProjectResource.resource_id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=401, detail="Resource not found")
    db_resource.update(**resource.dict(exclude_unset=True))
    db.commit()
    db.refresh(db_resource)
    return ProjectResourceResponse(
        resource_id=db_resource.resource_id,
        project_id=db_resource.project_id,
        title=db_resource.title,
        url=db_resource.url,
        type=db_resource.type,
        pinned=db_resource.pinned,
        created_by=UserDTO(
            user_id=db_resource.created_by,
            name=db_resource.created_by_user.name,
            role=db_resource.created_by_user.role,
            picture=db_resource.created_by_user.picture
        ),
        created_at=int(db_resource.created_at.timestamp()) if db_resource.created_at else None,
        last_updated=int(db_resource.last_updated.timestamp()) if db_resource.last_updated else None
    )

def delete_resource(db: Session, resource_id: str):
    db_resource = db.query(ProjectResource).filter(ProjectResource.resource_id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=401, detail="Resource not found")
    db.delete(db_resource)
    db.commit() 

def create_initiative_resource(db: Session, initiative_id: str, resource: ResourceCreate) -> InitiativeResourceResponse:
    db_resource = InitiativeResource(
        initiative_id=initiative_id,
        title=resource.title,
        url=resource.url,
        type=resource.type,
        created_by=resource.created_by,
        pinned=resource.pinned
    )
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return InitiativeResourceResponse(
        resource_id=db_resource.resource_id,
        initiative_id=db_resource.initiative_id,
        title=db_resource.title,
        url=db_resource.url,
        type=db_resource.type,
        pinned=db_resource.pinned,
        created_by=UserDTO(
            user_id=db_resource.created_by,
            name=db_resource.created_by_user.name,
            role=db_resource.created_by_user.role,
            picture=db_resource.created_by_user.picture,
            email=db_resource.created_by_user.email
        ),
        created_at=int(db_resource.created_at.timestamp()) if db_resource.created_at else None,
        last_updated=int(db_resource.last_updated.timestamp()) if db_resource.last_updated else None
    )

def get_initiative_resources(db: Session, initiative_id: str) -> List[InitiativeResourceResponse]:
    db_resources = db.query(InitiativeResource).filter(InitiativeResource.initiative_id == initiative_id).order_by(InitiativeResource.created_at.desc()).all()
    return [InitiativeResourceResponse(
        resource_id=resource.resource_id,   
        initiative_id=resource.initiative_id,
        title=resource.title,
        url=resource.url,
        type=resource.type,
        pinned=resource.pinned,
        created_by=UserDTO(
            user_id=resource.created_by,
            name=resource.created_by_user.name,
            role=resource.created_by_user.role,
            picture=resource.created_by_user.picture,
            email=resource.created_by_user.email
        ),
        created_at=int(resource.created_at.timestamp()) if resource.created_at else None,
        last_updated=int(resource.last_updated.timestamp()) if resource.last_updated else None
    ) for resource in db_resources]

def patch_initiative_resource(db: Session, initiative_id: str, resource_id: str, resource: ResourceUpdate):
    db_resource = db.query(InitiativeResource).filter(InitiativeResource.resource_id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=401, detail="Resource not found")
    db_resource.update(**resource.dict(exclude_unset=True))
    db.commit()
    db.refresh(db_resource)
    return InitiativeResourceResponse(
        resource_id=db_resource.resource_id,
        initiative_id=db_resource.initiative_id,
        title=db_resource.title,
        url=db_resource.url,
        type=db_resource.type,
        pinned=db_resource.pinned,
        created_by=UserDTO(
            user_id=db_resource.created_by,
            name=db_resource.created_by_user.name,
            role=db_resource.created_by_user.role,
            picture=db_resource.created_by_user.picture,
            email=db_resource.created_by_user.email
        ),
        created_at=int(db_resource.created_at.timestamp()) if db_resource.created_at else None,
        last_updated=int(db_resource.last_updated.timestamp()) if db_resource.last_updated else None
    )   

def delete_initiative_resource(db: Session, resource_id: str):
    db_resource = db.query(InitiativeResource).filter(InitiativeResource.resource_id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=401, detail="Resource not found")
    db.delete(db_resource)  
from sqlalchemy.orm import Session
from app.models.dependencies import InitiativeDependency, ProjectDependency, DependencyType
from app.schemas.dependencies import (
    InitiativeDependencyCreate,
    InitiativeDependencyResponse,
    ProjectDependencyCreate,
    ProjectDependencyResponse
)
from uuid import uuid4
from app.models.user import User
from app.dto.dtos import UserDTO, DependencyInitiativeDTO, DependencyProjectDTO
from typing import List
from fastapi import HTTPException
from app.models.initiative import Initiative
from app.models.project import Project

def create_initiative_dependency(
    db: Session,
    initiative_id: str,
    dependency: InitiativeDependencyCreate
) -> InitiativeDependencyResponse:
    # Create new dependency
    new_dependency = InitiativeDependency(
        dependency_id=str(uuid4()),
        type=dependency.type,
        source_initiative_id=initiative_id if dependency.type == DependencyType.DEPENDENCY_OF else dependency.initiative_id,
        target_initiative_id=dependency.initiative_id if dependency.type == DependencyType.DEPENDENCY_OF else initiative_id,
        created_by=dependency.created_by,
        status=dependency.status,
        description=dependency.description
    )
    
    # Check if dependency already exists
    existing = db.query(InitiativeDependency).filter(
        InitiativeDependency.source_initiative_id == new_dependency.source_initiative_id,
        InitiativeDependency.target_initiative_id == new_dependency.target_initiative_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Dependency already exists")
    
    db.add(new_dependency)
    db.commit()
    db.refresh(new_dependency)
    
    # Get related data for response
    created_by_user = db.query(User).filter(User.user_id == new_dependency.created_by).first()
    initiative = db.query(Initiative).filter(Initiative.initiative_id == dependency.initiative_id).first()
    
    return [InitiativeDependencyResponse(
        dependency_id=new_dependency.dependency_id,
        type=new_dependency.type,
        initiative=DependencyInitiativeDTO(
            initiative_id=initiative.initiative_id,
            title=initiative.title,
            status=initiative.status,
            owner=UserDTO(
                user_id=initiative.owner_id,
                name=initiative.owner.name,
                email=initiative.owner.email,
                role=initiative.owner.role,
                picture=initiative.owner.picture
            ) if initiative.owner else None
        ),
        status=new_dependency.status,
        created_at=int(new_dependency.created_at.timestamp()),
        last_updated=int(new_dependency.last_updated.timestamp()),
        created_by=UserDTO(
            user_id=created_by_user.user_id,
            name=created_by_user.name,
            email=created_by_user.email,
            role=created_by_user.role,
            picture=created_by_user.picture
        ),
        updated_by=UserDTO(
            user_id=new_dependency.updated_by,
            name=created_by_user.name,
            email=created_by_user.email,
            role=created_by_user.role,
            picture=created_by_user.picture
        ),
        description=new_dependency.description
    )]

def get_initiative_dependencies(
    db: Session,
    initiative_id: str
) -> List[InitiativeDependencyResponse]:
    dependencies = db.query(InitiativeDependency).filter(
        (InitiativeDependency.source_initiative_id == initiative_id) |
        (InitiativeDependency.target_initiative_id == initiative_id)
    ).all()
    
    responses = []
    for dep in dependencies:
        created_by_user = db.query(User).filter(User.user_id == dep.created_by).first()
        updated_by_user = db.query(User).filter(User.user_id == dep.updated_by).first()
        
        # If current initiative is source, show target initiative and vice versa
        is_current_source = dep.source_initiative_id == initiative_id
        related_initiative_id = dep.target_initiative_id if is_current_source else dep.source_initiative_id
        related_initiative = db.query(Initiative).filter(Initiative.initiative_id == related_initiative_id).first()
        
        # If we're the target, it means we depend on the source
        displayed_type = DependencyType.DEPENDS_ON if dep.target_initiative_id == initiative_id else DependencyType.DEPENDENCY_OF
        
        responses.append(InitiativeDependencyResponse(
            dependency_id=dep.dependency_id,
            type=displayed_type,
            initiative=DependencyInitiativeDTO(
                initiative_id=related_initiative.initiative_id,
                title=related_initiative.title,
                status=related_initiative.status,
                owner=UserDTO(
                    user_id=related_initiative.owner_id,
                    name=related_initiative.owner.name,
                    email=related_initiative.owner.email,
                    role=related_initiative.owner.role,
                    picture=related_initiative.owner.picture
                ) if related_initiative.owner else None
            ),
            status=dep.status,
            created_at=int(dep.created_at.timestamp()),
            last_updated=int(dep.last_updated.timestamp()),
            created_by=UserDTO(
                user_id=created_by_user.user_id,
                name=created_by_user.name,
                email=created_by_user.email,
                role=created_by_user.role,
                picture=created_by_user.picture
            ),
            updated_by=UserDTO(
                user_id=updated_by_user.user_id,
                name=updated_by_user.name,
                email=updated_by_user.email,
                role=updated_by_user.role,
                picture=updated_by_user.picture
            ) if updated_by_user else None,
            description=dep.description
        ))
    
    return responses

# Similar functions for projects
def create_project_dependency(
    db: Session,
    project_id: str,
    dependency: ProjectDependencyCreate
) -> ProjectDependencyResponse:
    new_dependency = ProjectDependency(
        dependency_id=str(uuid4()),
        type=dependency.type,
        source_project_id=project_id if dependency.type == DependencyType.DEPENDENCY_OF else dependency.project_id,
        target_project_id=dependency.project_id if dependency.type == DependencyType.DEPENDENCY_OF else project_id,
        created_by=dependency.created_by,
        status=dependency.status,
        description=dependency.description
    )
    
    existing = db.query(ProjectDependency).filter(
        ProjectDependency.source_project_id == new_dependency.source_project_id,
        ProjectDependency.target_project_id == new_dependency.target_project_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Dependency already exists")
    
    db.add(new_dependency)
    db.commit()
    db.refresh(new_dependency)
    
    created_by_user = db.query(User).filter(User.user_id == new_dependency.created_by).first()
    
    # Use the same logic as get_project_dependencies
    is_current_source = new_dependency.source_project_id == project_id
    related_project = new_dependency.target_project if is_current_source else new_dependency.source_project
    
    return [ProjectDependencyResponse(
        dependency_id=new_dependency.dependency_id,
        type=new_dependency.type,
        project=DependencyProjectDTO(
            project_id=related_project.project_id,
            title=related_project.title,
            status=related_project.status,
            owner=UserDTO(
                user_id=related_project.dri_id,
                name=related_project.dri.name,
                email=related_project.dri.email,
                role=related_project.dri.role,
                picture=related_project.dri.picture
            ) if related_project.dri else None
        ),
        status=new_dependency.status,
        created_at=int(new_dependency.created_at.timestamp()),
        last_updated=int(new_dependency.last_updated.timestamp()),
        created_by=UserDTO(
            user_id=created_by_user.user_id,
            name=created_by_user.name,
            email=created_by_user.email,
            role=created_by_user.role,
            picture=created_by_user.picture
        ),
        updated_by=UserDTO(
            user_id=new_dependency.updated_by,
            name=created_by_user.name,
            email=created_by_user.email,
            role=created_by_user.role,
            picture=created_by_user.picture
        ),
        description=new_dependency.description
    )]

def get_project_dependencies(
    db: Session,
    project_id: str
) -> List[ProjectDependencyResponse]:
    dependencies = db.query(ProjectDependency).filter(
        (ProjectDependency.source_project_id == project_id) |
        (ProjectDependency.target_project_id == project_id)
    ).all()
    
    responses = []
    for dep in dependencies:
        created_by_user = db.query(User).filter(User.user_id == dep.created_by).first()
        updated_by_user = db.query(User).filter(User.user_id == dep.updated_by).first()
        
        # If current project is source, show target project and vice versa
        is_current_source = dep.source_project_id == project_id
        related_project = dep.target_project if is_current_source else dep.source_project
        # If we're the target, it means we depend on the source
        displayed_type = DependencyType.DEPENDS_ON if dep.target_project_id == project_id else DependencyType.DEPENDENCY_OF
        
        responses.append(ProjectDependencyResponse(
            dependency_id=dep.dependency_id,
            type=displayed_type,
            project=DependencyProjectDTO(
                project_id=related_project.project_id,
                title=related_project.title,
                status=related_project.status,
                dri=UserDTO(
                    user_id=related_project.dri_id,
                    name=related_project.dri.name,
                    email=related_project.dri.email,
                    role=related_project.dri.role,
                    picture=related_project.dri.picture
                ) if related_project.dri else None
            ),
            status=dep.status,
            created_at=int(dep.created_at.timestamp()),
            last_updated=int(dep.last_updated.timestamp()),
            created_by=UserDTO(
                user_id=created_by_user.user_id,
                name=created_by_user.name,
                email=created_by_user.email,
                role=created_by_user.role,
                picture=created_by_user.picture
            ),
            updated_by=UserDTO(
                user_id=updated_by_user.user_id,
                name=updated_by_user.name,
                email=updated_by_user.email,
                role=updated_by_user.role,
                picture=updated_by_user.picture
            ) if updated_by_user else None,
            description=dep.description
        ))
    
    return responses

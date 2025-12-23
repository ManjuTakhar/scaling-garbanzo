from sqlalchemy.orm import Session
from app.models.updates import ProjectUpdate, InitiativeUpdate
from app.schemas.updates import UpdateCreate, ProjectUpdateResponse, InitiativeUpdateResponse
from typing import List
from app.models.user import User
from app.dto.dtos import UserDTO
from sqlalchemy.orm import joinedload

def create_project_update(db: Session, project_id: str, update: UpdateCreate) -> ProjectUpdateResponse:
    db_update = ProjectUpdate(
        project_id=project_id,
        content=update.content,
        created_by=update.created_by,
        current_status = update.current_status
    )
    db.add(db_update)
    db.commit()
    db.refresh(db_update)
    posted_by = db.query(User).filter(User.user_id == update.created_by).first()
    return ProjectUpdateResponse(
        update_id=db_update.update_id,
        project_id=db_update.project_id,
        content=db_update.content,
        created_by=UserDTO(
            user_id=posted_by.user_id,
            email=posted_by.email,
            name=posted_by.name,
            role=posted_by.role,
            picture=posted_by.picture
        ),
        current_status=db_update.current_status,
        created_at=int(db_update.created_at.timestamp()) if db_update.created_at else None
    ) if db_update else None

def get_project_updates(db: Session, project_id: str) -> List[ProjectUpdateResponse]:
       updates = db.query(ProjectUpdate)\
           .options(joinedload(ProjectUpdate.posted_by))\
           .filter(ProjectUpdate.project_id == project_id)\
           .order_by(ProjectUpdate.created_at.desc())\
           .all()

       return [ProjectUpdateResponse(
           update_id=update.update_id,
           project_id=update.project_id,
           content=update.content,
           created_by=UserDTO(
               user_id=update.posted_by.user_id,
               email=update.posted_by.email,
               name=update.posted_by.name,
               role=update.posted_by.role,
               picture=update.posted_by.picture
           ),
           current_status=update.current_status,
           created_at=int(update.created_at.timestamp()) if update.created_at else None,
       ) for update in updates] if updates else []

def create_initiative_update(db: Session, initiative_id: str, update: UpdateCreate) -> InitiativeUpdateResponse:
    db_update = InitiativeUpdate(
        initiative_id=initiative_id,
        content=update.content,
        created_by=update.created_by,
        current_status=update.current_status
    )
    db.add(db_update)
    db.commit()
    db.refresh(db_update)
    posted_by = db.query(User).filter(User.user_id == update.created_by).first()
    return InitiativeUpdateResponse(
        update_id=db_update.update_id,
        initiative_id=db_update.initiative_id,
        content=db_update.content,
        created_by=UserDTO(
            user_id=posted_by.user_id,
            email=posted_by.email,
            name = posted_by.name,   
            role=posted_by.role,
            picture=posted_by.picture
        ),
        current_status=db_update.current_status,
        created_at=int(db_update.created_at.timestamp()) if db_update.created_at else None,
    ) if db_update else None

def get_initiative_updates(db: Session, initiative_id: str) -> List[InitiativeUpdateResponse]:
    updates = db.query(InitiativeUpdate)\
        .filter(InitiativeUpdate.initiative_id == initiative_id)\
        .order_by(InitiativeUpdate.created_at.desc())\
        .all()
    return [InitiativeUpdateResponse(
        update_id=update.update_id,
        initiative_id=update.initiative_id,
        content=update.content,
        created_by=UserDTO(
            user_id=update.posted_by.user_id,
            email=update.posted_by.email,
            name = update.posted_by.name,   
            role=update.posted_by.role,
            picture=update.posted_by.picture
        ),
        current_status=update.current_status,
        created_at=int(update.created_at.timestamp()) if update.created_at else None,
    ) for update in updates] if updates else []

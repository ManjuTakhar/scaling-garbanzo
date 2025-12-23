from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List
from app.schemas.updates import UpdateCreate, ProjectUpdateResponse, InitiativeUpdateResponse
from app.schemas.project import ProjectUpdate as UpdateProjectRequest
from app.schemas.initiative import InitiativeUpdate as UpdateInitiativeRequest
from app.crud import updates as crud_updates
from app.crud import initiative as crud_initiative
from app.crud import project as crud_project
from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.crud import user as user_crud
from app.services.slack_service import SlackService
from app.core.config import settings

router = APIRouter()

@router.post("/projects/{project_id}/updates", response_model=ProjectUpdateResponse)
async def create_project_update(
    project_id: str,
    update: UpdateCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...),
):
    """Create a project update. Auth required."""
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    
    # Get project details
    project = crud_project.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_url = f"{settings.FRONTEND_URL}/projects/{project_id}"

    # Use the authenticated user's tenant_id instead of a hardcoded value
    update.tenant_id = user.tenant_id
    project_update = crud_updates.create_project_update(db=db, project_id=project_id, update=update)

    if update.current_status:
        crud_project.update_project(db, project_id=project_id, project=UpdateProjectRequest(status=update.current_status))

    if update.channels_to_post:
        slack_service = SlackService(db=db)
        slack_errors = []
        
        # Create enhanced message data
        enhanced_message_data = {
            "content": update.content,
            "metadata": {
                "project_name": project.title,
                "status": update.current_status,
                "updated_by": current_user["name"],
                "update_type": "project",
                "project_id": project_id,
                "project_url": project_url
            }
        }

        for channel in update.channels_to_post:
            try:
                response = await slack_service.post_message_to_channel(
                    update.tenant_id, 
                    channel, 
                    enhanced_message_data
                )
            except Exception as e:
                slack_errors.append(f"Failed to post to channel {channel}: {str(e)}")
                continue
        if slack_errors:
            print(f"Some Slack messages failed to post: {', '.join(slack_errors)}")
    
    return project_update

@router.get("/projects/{project_id}/updates", response_model=List[ProjectUpdateResponse])
def list_project_updates(project_id: str, 
                         db: Session = Depends(get_db),
                         current_user: dict = Depends(get_current_user),
                         authorization: str = Header(...)):
    """List project updates. Auth required."""
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return crud_updates.get_project_updates(db=db, project_id=project_id)

@router.post("/initiatives/{initiative_id}/updates", response_model=InitiativeUpdateResponse)
async def create_initiative_update(
    initiative_id: str,
    update: UpdateCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...),
):
    """Create an initiative update. Auth required."""
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    
    # Get initiative details
    initiative = crud_initiative.get_initiative(db, initiative_id)
    if not initiative:
        raise HTTPException(status_code=404, detail="Initiative not found")

    # Create initiative URL
    initiative_url = f"{settings.FRONTEND_URL}/initiatives/{initiative_id}"

    # Use the authenticated user's tenant_id instead of a hardcoded value
    update.tenant_id = user.tenant_id
    initiative_update = crud_updates.create_initiative_update(db=db, initiative_id=initiative_id, update=update)

    if update.current_status:
        crud_initiative.update_initiative(db, initiative_id=initiative_id, initiative=UpdateInitiativeRequest(status=update.current_status))

    if update.channels_to_post:
        slack_service = SlackService(db=db)
        slack_errors = []
        
        # Create enhanced message data with initiative URL
        enhanced_message_data = {
            "content": update.content,
            "metadata": {
                "name": initiative.title,
                "url": initiative_url,
                "status": update.current_status,
                "updated_by": current_user["name"],
                "update_type": "initiative",
                "id": initiative_id
            }
        }

        for channel in update.channels_to_post:
            try:
                response = await slack_service.post_message_to_channel(
                    update.tenant_id, 
                    channel, 
                    enhanced_message_data
                )
            except Exception as e:
                slack_errors.append(f"Failed to post to channel {channel}: {str(e)}")
                continue
        if slack_errors:
            print(f"Some Slack messages failed to post: {', '.join(slack_errors)}")
    
    return initiative_update

@router.get("/initiatives/{initiative_id}/updates", response_model=List[InitiativeUpdateResponse])
def list_initiative_updates(initiative_id: str, 
                            db: Session = Depends(get_db),
                            current_user: dict = Depends(get_current_user),
                            authorization: str = Header(...)):
    """List initiative updates. Auth required."""
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return crud_updates.get_initiative_updates(db=db, initiative_id=initiative_id) 

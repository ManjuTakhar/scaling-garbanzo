from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.project_interactions import (
    ProjectInteractionResponse,
    ProjectCommentCreate,
    ProjectReactionCreate
)
from app.crud import project_interactions as crud
from app.crud import user as user_crud
from fastapi import HTTPException, Header   
from app.api.dependencies import get_current_user, get_current_user_with_workspace

router = APIRouter()

@router.post("/projects/{project_id}/updates/{update_id}/comment", response_model=ProjectInteractionResponse)
def create_project_comment(
    project_id: str,
    update_id: str,
    comment: ProjectCommentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...)
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    crud.create_project_comment(
        db=db,
        comment=comment,
        created_by=comment.created_by,
        update_id=update_id
    )
    return crud.get_project_interactions(db=db, update_id=update_id)

@router.get("/projects/{project_id}/updates/{update_id}/interactions", response_model=ProjectInteractionResponse)
def get_project_interactions(
    project_id: str,
    update_id: str,
    db: Session = Depends(get_db),
    user_context: dict = Depends(get_current_user_with_workspace),
    authorization: str = Header(...)
):
    return crud.get_project_interactions(db=db, update_id=update_id)

@router.post("/projects/{project_id}/updates/{update_id}/react", response_model=ProjectInteractionResponse)
def react_to_project_update(
    project_id: str,
    update_id: str,
    reaction: ProjectReactionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...)
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    crud.add_project_reaction(
        db=db,
        update_id=update_id,
        reacted_by=reaction.reacted_by,
        reaction=reaction
    )
    return crud.get_project_interactions(db=db, update_id=update_id)

@router.put("/projects/{project_id}/updates/{update_id}/comments/{comment_id}", response_model=ProjectInteractionResponse)
def update_project_comment(
    project_id: str,
    update_id: str,
    comment_id: str,
    comment: ProjectCommentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...)
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    crud.update_project_comment(db=db, comment_id=comment_id, comment=comment)
    return crud.get_project_interactions(db=db, update_id=update_id)

@router.delete("/projects/{project_id}/updates/{update_id}/comments/{comment_id}", response_model=ProjectInteractionResponse)
def delete_project_comment(
    project_id: str,
    update_id: str,
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...)
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    crud.delete_project_comment(db=db, comment_id=comment_id)
    return crud.get_project_interactions(db=db, update_id=update_id)

@router.put("/projects/{project_id}/updates/{update_id}/react/{reaction_id}", response_model=ProjectReactionCreate)
def update_project_reaction_endpoint(
    project_id: str,
    update_id: str,
    reaction_id: str,
    reaction: ProjectReactionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...)
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return crud.update_project_reaction(db=db, reaction_id=reaction_id, reaction=reaction)

@router.delete("/projects/{project_id}/updates/{update_id}/react/{reaction_id}", response_model=None)
def delete_project_reaction_endpoint(
    project_id: str,
    update_id: str,
    reaction_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...)
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return crud.delete_project_reaction(db=db, reaction_id=reaction_id)


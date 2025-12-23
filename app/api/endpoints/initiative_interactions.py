from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.initiative_interactions import (
    InitiativeInteractionResponse,
    InitiativeCommentCreate,
    InitiativeReactionCreate
)
from app.crud import initiative_interactions as crud
from app.api.dependencies import get_current_user
from fastapi import Header
from app.crud import user as user_crud

router = APIRouter()

@router.post("/initiatives/{initiative_id}/updates/{update_id}/comment", response_model=InitiativeInteractionResponse)
def create_initiative_comment(
    update_id: str,
    comment: InitiativeCommentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...)

):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    crud.create_initiative_comment(
        db=db,
        comment=comment,
        created_by=comment.created_by,
        update_id=update_id
    )
    return crud.get_initiative_interactions(db=db, update_id=update_id)

@router.get("/initiatives/{initiative_id}/updates/{update_id}/interactions", response_model=InitiativeInteractionResponse)
def get_initiative_interactions(
    initiative_id: str,
    update_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...)    
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    return crud.get_initiative_interactions(db=db, update_id=update_id)

@router.post("/initiatives/{initiative_id}/updates/{update_id}/react", response_model=InitiativeInteractionResponse)
def react_to_initiative_update(
    initiative_id: str,
    update_id: str,
    reaction: InitiativeReactionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...)
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    crud.add_initiative_reaction(
        db=db,
        update_id=update_id,
        reacted_by=reaction.reacted_by,
        reaction=reaction
    )
    return crud.get_initiative_interactions(db=db, update_id=update_id)

@router.put("/initiatives/{initiative_id}/updates/{update_id}/comments/{comment_id}", response_model=InitiativeInteractionResponse)
def update_initiative_comment(
    initiative_id: str,
    update_id: str,
    comment_id: str,
    comment: InitiativeCommentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...)
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    crud.update_initiative_comment(db=db, comment_id=comment_id, comment=comment)
    return crud.get_initiative_interactions(db=db, update_id=update_id)

@router.delete("/initiatives/{initiative_id}/updates/{update_id}/comments/{comment_id}", response_model=InitiativeInteractionResponse)
def delete_initiative_comment(
    initiative_id: str,
    update_id: str,
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...)
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    crud.delete_initiative_comment(db=db, comment_id=comment_id)
    return crud.get_initiative_interactions(db=db, update_id=update_id)

@router.put("/initiatives/{initiative_id}/updates/{update_id}/react/{reaction_id}", response_model=InitiativeInteractionResponse)
def update_initiative_reaction(
    initiative_id: str,
    update_id: str,
    reaction_id: str,
    reaction: InitiativeReactionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...)
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    crud.update_initiative_reaction(db=db, reaction_id=reaction_id, reaction=reaction)
    return crud.get_initiative_interactions(db=db, update_id=update_id)

@router.delete("/initiatives/{initiative_id}/updates/{update_id}/react/{reaction_id}", response_model=InitiativeInteractionResponse)
def delete_initiative_reaction(
    initiative_id: str,
    update_id: str,
    reaction_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(...)
):
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    crud.delete_initiative_reaction(db=db, reaction_id=reaction_id)
    return crud.get_initiative_interactions(db=db, update_id=update_id)

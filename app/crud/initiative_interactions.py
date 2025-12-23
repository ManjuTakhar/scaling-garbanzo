from sqlalchemy.orm import Session
from app.models.initiative_interactions import InitiativeComment, InitiativeReaction
from app.schemas.initiative_interactions import InitiativeCommentCreate, InitiativeReactionCreate, InitiativeInteractionResponse, InitiativeCommentResponse, InitiativeReactionResponse
import uuid
from fastapi import HTTPException
from app.models.user import User
from app.dto.dtos import UserDTO


def create_initiative_comment(
    db: Session,
    comment: InitiativeCommentCreate,
    created_by: str,
    update_id: str
):
    db_comment = InitiativeComment(
        comment_id=str(uuid.uuid4()),
        content=comment.content,
        created_by=created_by,
        update_id=update_id
    )
    user = db.query(User).filter(User.user_id == created_by).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return InitiativeCommentResponse(
        comment_id=db_comment.comment_id,
        content=db_comment.content,
        created_by=UserDTO(
            user_id=db_comment.created_by_user.user_id,
            name=db_comment.created_by_user.name,
            email=db_comment.created_by_user.email,
            role=db_comment.created_by_user.role,
            picture=db_comment.created_by_user.picture
        ),
        created_at=int(db_comment.created_at.timestamp()) if db_comment.created_at else None,
        update_id=db_comment.update_id
    )


def get_initiative_interactions(db: Session, update_id: str):
    comments = db.query(InitiativeComment).filter(
        InitiativeComment.update_id == update_id
    ).all()
    reactions = db.query(InitiativeReaction).filter(
        InitiativeReaction.update_id == update_id
    ).all()
    comments = [InitiativeCommentResponse(
        comment_id=comment.comment_id,
        content=comment.content,
        created_by=UserDTO(
            user_id=comment.created_by_user.user_id,
            name=comment.created_by_user.name,
            email=comment.created_by_user.email,
            role=comment.created_by_user.role,
            picture=comment.created_by_user.picture
        ),
        created_at=int(comment.created_at.timestamp()) if comment.created_at else None,
        update_id=comment.update_id
    ) for comment in comments] if comments else []
    reactions = [InitiativeReactionResponse(
        reaction_id=reaction.reaction_id,
        reaction_type=reaction.reaction_type,
        reacted_by=UserDTO(
            user_id=reaction.reacted_by_user.user_id,
            name=reaction.reacted_by_user.name,
            email=reaction.reacted_by_user.email,
            role=reaction.reacted_by_user.role,
            picture=reaction.reacted_by_user.picture
        ),
        created_at=int(reaction.created_at.timestamp()) if reaction.created_at else None,
        update_id=reaction.update_id
    ) for reaction in reactions] if reactions else []
    return InitiativeInteractionResponse(comments=comments, reactions=reactions)


def add_initiative_reaction(
    db: Session,
    update_id: str,
    reacted_by: str,
    reaction: InitiativeReactionCreate
):
    existing_reaction = db.query(InitiativeReaction).filter(
        InitiativeReaction.update_id == update_id,
        InitiativeReaction.reacted_by == reacted_by,
        InitiativeReaction.reaction_type == reaction.reaction_type
    ).first()
    
    if existing_reaction:
        db.delete(existing_reaction)
        db.commit()
        return None  # Remove reaction if it's the same type by the same user
    
    new_reaction = InitiativeReaction(
        reaction_id=str(uuid.uuid4()),
        update_id=update_id,
        reacted_by=reacted_by,
        reaction_type=reaction.reaction_type
    )
    user = db.query(User).filter(User.user_id == reacted_by).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    db.add(new_reaction)
    db.commit()
    db.refresh(new_reaction)
    return InitiativeReactionResponse(
        reaction_id=new_reaction.reaction_id,
        reaction_type=new_reaction.reaction_type,
        update_id=new_reaction.update_id,
        created_at=int(new_reaction.created_at.timestamp()) if new_reaction.created_at else None,
        reacted_by=UserDTO(
            user_id=new_reaction.reacted_by_user.user_id,
            name=new_reaction.reacted_by_user.name,
            email=new_reaction.reacted_by_user.email,
            role=new_reaction.reacted_by_user.role,
            picture=new_reaction.reacted_by_user.picture
        ),
    )


def update_initiative_comment(
    db: Session,
    comment_id: str,
    comment: InitiativeCommentCreate
):
    db_comment = db.query(InitiativeComment).filter(
        InitiativeComment.comment_id == comment_id
    ).first()
    
    if not db_comment:
        raise HTTPException(status_code=401, detail="Comment not found")
    
    db_comment.content = comment.content
    db.commit()
    db.refresh(db_comment)
    return InitiativeCommentResponse(
        comment_id=db_comment.comment_id,
        content=db_comment.content,
        created_by=UserDTO(
            user_id=db_comment.created_by_user.user_id,
            name=db_comment.created_by_user.name,
            email=db_comment.created_by_user.email,
            role=db_comment.created_by_user.role,
            picture=db_comment.created_by_user.picture
        ),
        created_at=int(db_comment.created_at.timestamp()) if db_comment.created_at else None,
        update_id=db_comment.update_id
    )


def delete_initiative_comment(db: Session, comment_id: str):
    db_comment = db.query(InitiativeComment).filter(
        InitiativeComment.comment_id == comment_id
    ).first()
    
    if not db_comment:
        raise HTTPException(status_code=401, detail="Comment not found")
    
    db.delete(db_comment)
    db.commit()
    return None

def update_initiative_reaction(
    db: Session,
    reaction_id: str,
    reaction: InitiativeReactionCreate
):
    db_reaction = db.query(InitiativeReaction).filter(
        InitiativeReaction.reaction_id == reaction_id
    ).first()
    
    if not db_reaction:
        raise HTTPException(status_code=401, detail="Reaction not found")
    
    db_reaction.reaction_type = reaction.reaction_type
    db.commit()
    db.refresh(db_reaction)
    return InitiativeReactionResponse(
        reaction_id=db_reaction.reaction_id,
        reaction_type=db_reaction.reaction_type,
        update_id=db_reaction.update_id,
        created_at=int(db_reaction.created_at.timestamp()) if db_reaction.created_at else None,
        reacted_by=UserDTO(
            user_id=db_reaction.reacted_by_user.user_id,
            name=db_reaction.reacted_by_user.name,
            email=db_reaction.reacted_by_user.email,
            role=db_reaction.reacted_by_user.role,
            picture=db_reaction.reacted_by_user.picture
        ),
    )


def delete_initiative_reaction(db: Session, reaction_id: str):
    db_reaction = db.query(InitiativeReaction).filter(
        InitiativeReaction.reaction_id == reaction_id
    ).first()
    
    if not db_reaction:
        raise HTTPException(status_code=401, detail="Reaction not found")
    
    db.delete(db_reaction)
    db.commit()
    return None
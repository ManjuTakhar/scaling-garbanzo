from sqlalchemy.orm import Session
from app.models.project_interactions import ProjectComment, ProjectReaction
from app.schemas.project_interactions import ProjectCommentCreate, ProjectReactionCreate, ProjectInteractionResponse, ProjectCommentResponse, ProjectReactionResponse
import uuid
from fastapi import HTTPException
from app.models.user import User
from app.dto.dtos import UserDTO


def create_project_comment(
    db: Session,
    comment: ProjectCommentCreate,
    created_by: str,
    update_id: str
):
    user = db.query(User).filter(User.user_id == created_by).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    db_comment = ProjectComment(
        comment_id=str(uuid.uuid4()),
        content=comment.content,
        created_by=created_by,
        update_id=update_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return ProjectCommentResponse(
        comment_id=db_comment.comment_id,
        content=db_comment.content,
        created_by=UserDTO(
            user_id=db_comment.created_by,
            name=user.name,
            email=user.email,
            role=user.role,
            picture=user.picture
        ),
        created_at=int(db_comment.created_at.timestamp()) if db_comment.created_at else None,
        update_id=db_comment.update_id
    )


def get_project_interactions(db: Session, update_id: str):
    comments = db.query(ProjectComment).filter(
        ProjectComment.update_id == update_id
    ).all()
    reactions = db.query(ProjectReaction).filter(
        ProjectReaction.update_id == update_id
    ).all()
    comments = [ProjectCommentResponse(
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
    reactions = [ProjectReactionResponse(
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
    return ProjectInteractionResponse(comments=comments, reactions=reactions)

def add_project_reaction(
    db: Session,
    update_id: str,
    reacted_by: str,
    reaction: ProjectReactionCreate
):
    existing_reaction = db.query(ProjectReaction).filter(
        ProjectReaction.update_id == update_id,
        ProjectReaction.reacted_by == reacted_by,
        ProjectReaction.reaction_type == reaction.reaction_type
    ).first()
    
    if existing_reaction:
        db.delete(existing_reaction)
        db.commit()
        return None  # Remove reaction if it's the same type by the same user
    
    user = db.query(User).filter(User.user_id == reacted_by).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    new_reaction = ProjectReaction(
        reaction_id=str(uuid.uuid4()),
        update_id=update_id,
        reacted_by=reacted_by,
        reaction_type=reaction.reaction_type
    )
    db.add(new_reaction)
    db.commit()
    db.refresh(new_reaction)
    return ProjectReactionResponse(
        reaction_id=new_reaction.reaction_id,
        reaction_type=new_reaction.reaction_type,
        reacted_by=UserDTO(
            user_id=new_reaction.reacted_by_user.user_id,
            name=new_reaction.reacted_by_user.name,
            email=new_reaction.reacted_by_user.email,
            role=new_reaction.reacted_by_user.role,
            picture=new_reaction.reacted_by_user.picture
        ),
        created_at=int(new_reaction.created_at.timestamp()) if new_reaction.created_at else None,
        update_id=new_reaction.update_id
    )


def update_project_comment(
    db: Session,
    comment_id: str,
    comment: ProjectCommentCreate
):
    db_comment = db.query(ProjectComment).filter(
        ProjectComment.comment_id == comment_id
    ).first()
    
    if not db_comment:
        raise HTTPException(status_code=401, detail="Comment not found")
    
    db_comment.content = comment.content
    db.commit()
    db.refresh(db_comment)
    return ProjectCommentResponse(
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


def delete_project_comment(db: Session, comment_id: str):
    db_comment = db.query(ProjectComment).filter(
        ProjectComment.comment_id == comment_id
    ).first()
    
    if not db_comment:
        raise HTTPException(status_code=401, detail="Comment not found")
    
    db.delete(db_comment)
    db.commit()
    return None

def update_project_reaction(
    db: Session,
    reaction_id: str,
    reaction: ProjectReactionCreate
):
    db_reaction = db.query(ProjectReaction).filter(
        ProjectReaction.reaction_id == reaction_id
    ).first()
    
    if not db_reaction:
        raise HTTPException(status_code=401, detail="Reaction not found")
    
    db_reaction.reaction_type = reaction.reaction_type
    db.commit()
    db.refresh(db_reaction)
    return ProjectReactionResponse(
        reaction_id=db_reaction.reaction_id,
        reaction_type=db_reaction.reaction_type,
        reacted_by=UserDTO(
            user_id=db_reaction.reacted_by_user.user_id,
            name=db_reaction.reacted_by_user.name,
            email=db_reaction.reacted_by_user.email,
            role=db_reaction.reacted_by_user.role,
            picture=db_reaction.reacted_by_user.picture
        ),
        created_at=int(db_reaction.created_at.timestamp()) if db_reaction.created_at else None,
        update_id=db_reaction.update_id
    )

def delete_project_reaction(db: Session, reaction_id: str):
    db_reaction = db.query(ProjectReaction).filter(
        ProjectReaction.reaction_id == reaction_id
    ).first()
    
    if not db_reaction:
        raise HTTPException(status_code=401, detail="Reaction not found")
    
    db.delete(db_reaction)
    db.commit()
    return None

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.schemas.issue_interactions import (
    IssueInteractionResponse,
    IssueCommentCreate,
    CommentReactionCreate,
    CommentReactionSummary,
    IssueCommentResponse
)
from app.crud import issue_interactions as crud


router = APIRouter()


@router.post("/issues/{issue_id}/comments", response_model=IssueCommentResponse)
def create_issue_comment(
    issue_id: str,
    comment: IssueCommentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return crud.create_issue_comment(
        db=db,
        comment=comment,
        created_by=comment.created_by,
        issue_id=issue_id
    )


@router.get(
    "/issues/{issue_id}/comments",
    response_model=IssueInteractionResponse,
    summary="Get all comments with reactions, reply counts & last‑reply timestamp"
)
def get_issue_comment_interactions(
    issue_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return crud.get_issue_interactions(db=db, issue_id=issue_id)


@router.post(
    "/issues/{issue_id}/comments/{comment_id}/react",
    response_model=List[CommentReactionSummary],
    summary="Toggle a reaction on a comment and return updated counts"
)
def react_to_comment(
    issue_id: str,
    comment_id: str,
    payload: CommentReactionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    crud.toggle_comment_reaction(
        db=db,
        comment_id=comment_id,
        reacted_by=payload.created_by,
        reaction_type=payload.reaction_type,
    )
    return crud.get_comment_reaction_summary(db, comment_id)


@router.put(
    "/issues/{issue_id}/comments/{comment_id}",
    response_model=IssueInteractionResponse,
    summary="Update a comment and return the updated comment list"
)
def update_comment(
    issue_id: str,
    comment_id: str,
    payload: IssueCommentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    crud.update_issue_comment(
        db=db,
        issue_id=issue_id,
        comment_id=comment_id,
        comment=payload
    )
    return crud.get_issue_interactions(db=db, issue_id=issue_id)


@router.delete(
    "/issues/{issue_id}/comments/{comment_id}",
    response_model=IssueInteractionResponse,
    summary="Delete a comment and return the updated comment list"
)
def delete_comment(
    issue_id: str,
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    crud.delete_issue_comment(
        db=db,
        issue_id=issue_id,
        comment_id=comment_id
    )
    return crud.get_issue_interactions(db=db, issue_id=issue_id)


@router.get(
    "/issues/{issue_id}/comments/{comment_id}/replies",
    response_model=IssueInteractionResponse,
    summary="Fetch all direct replies to a comment"
)
def list_comment_replies(
    issue_id: str,
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return crud.get_replies(db=db, comment_id=comment_id)



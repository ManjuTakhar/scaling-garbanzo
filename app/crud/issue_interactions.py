from sqlalchemy.orm import Session
from app.models.issue_interactions import IssueComment, CommentReaction
from app.schemas.issue_interactions import IssueCommentCreate, IssueInteractionResponse, IssueCommentResponse, CommentReactionSummary
import uuid
from fastapi import HTTPException
from app.models.user import User
from app.dto.dtos import UserDTO
from sqlalchemy import func


def get_issue_interactions(db: Session, issue_id: str):
    comments = (
        db.query(IssueComment)
          .filter(
              IssueComment.issue_id == issue_id,
              IssueComment.parent_comment_id.is_(None)
          )
          .order_by(IssueComment.created_at.asc())
          .all()
    )

    enriched = []
    for c in comments:
        raw = (
            db.query(
                CommentReaction.reaction_type,
                func.count(CommentReaction.id).label("reactions_count")
            )
            .filter_by(comment_id=c.id)
            .group_by(CommentReaction.reaction_type)
            .all()
        )
        reactions = [
            CommentReactionSummary(reaction_type=r[0], count=r[1])
            for r in raw
        ]

        stats = (
            db.query(
                func.count(IssueComment.id).label("replies_count"),
                func.max(IssueComment.created_at).label("last_reply_at")
            )
            .filter(IssueComment.parent_comment_id == c.id)
            .one()
        )
        replies_count = stats.replies_count or 0
        last_reply_at = int(stats.last_reply_at.timestamp()) if stats.last_reply_at else None

        # Fetch only needed user fields to avoid schema mismatch (no workspace_id)
        created_user = db.query(User.user_id, User.name, User.email, User.picture).filter(User.user_id == c.created_by).first()

        enriched.append(IssueCommentResponse(
            id=c.id,
            content=c.content,
            created_by=UserDTO(
                user_id=created_user.user_id if created_user else c.created_by,
                name=created_user.name if created_user else None,
                email=created_user.email if created_user else None,
                picture=created_user.picture if created_user else None
            ),
            created_at=int(c.created_at.timestamp()) if c.created_at else None,
            issue_id=c.issue_id,
            reactions=reactions,
            replies_count=replies_count,
            last_reply_at=last_reply_at
        ))

    return IssueInteractionResponse(comments=enriched)


def toggle_comment_reaction(
    db: Session,
    comment_id: str,
    reacted_by: str,
    reaction_type: str
):
    existing = db.query(CommentReaction).filter_by(
        comment_id=comment_id,
        created_by=reacted_by,
        reaction_type=reaction_type
    ).first()
    if existing:
        db.delete(existing)
    else:
        db.add(CommentReaction(
            id=str(uuid.uuid4()),
            comment_id=comment_id,
            created_by=reacted_by,
            reaction_type=reaction_type
        ))
    db.commit()


def get_comment_reaction_summary(db: Session, comment_id: str):
    rows = (
        db.query(
            CommentReaction.reaction_type,
            func.count(CommentReaction.id).label("count")
        )
        .filter_by(comment_id=comment_id)
        .group_by(CommentReaction.reaction_type)
        .all()
    )
    return [
        CommentReactionSummary(reaction_type=r[0], count=r[1])
        for r in rows
    ]


def create_issue_comment(
    db: Session,
    comment: IssueCommentCreate,
    created_by: str,
    issue_id: str
):
    # user_id column is user_id in syncup-core
    user = db.query(User.user_id, User.name, User.email, User.picture).filter(User.user_id == created_by).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if comment.parent_comment_id:
        parent_comment = db.query(IssueComment).filter(IssueComment.id == comment.parent_comment_id).first()
        if not parent_comment:
            raise HTTPException(status_code=401, detail="Parent comment not found")

    db_comment = IssueComment(
        id=str(uuid.uuid4()),
        content=comment.content,
        created_by=created_by,
        issue_id=issue_id,
        parent_comment_id=comment.parent_comment_id if comment.parent_comment_id else None
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return IssueCommentResponse(
        id=db_comment.id,
        content=db_comment.content,
        created_by=UserDTO(
            user_id=user.user_id if user else db_comment.created_by,
            name=user.name if user else None,
            email=user.email if user else None,
            picture=user.picture if user else None
        ),
        created_at=int(db_comment.created_at.timestamp()) if db_comment.created_at else None,
        issue_id=db_comment.issue_id
    )


def get_replies(db: Session, comment_id: str) -> IssueInteractionResponse:
    replies = (
        db.query(IssueComment)
          .filter(IssueComment.parent_comment_id == comment_id)
          .order_by(IssueComment.created_at.asc())
          .all()
    )

    enriched = []
    for r in replies:
        raw = (
            db.query(
                CommentReaction.reaction_type,
                func.count(CommentReaction.id).label("cnt")
            )
            .filter_by(comment_id=r.id)
            .group_by(CommentReaction.reaction_type)
            .all()
        )
        reactions = [
            CommentReactionSummary(reaction_type=rt, count=cnt)
            for rt, cnt in raw
        ]

        reply_user = db.query(User.user_id, User.name, User.email, User.picture).filter(User.user_id == r.created_by).first()

        enriched.append(IssueCommentResponse(
            id=r.id,
            content=r.content,
            created_by=UserDTO(
                user_id=reply_user.user_id if reply_user else r.created_by,
                name=reply_user.name if reply_user else None,
                email=reply_user.email if reply_user else None,
                picture=reply_user.picture if reply_user else None
            ),
            created_at=int(r.created_at.timestamp()) if r.created_at else None,
            issue_id=r.issue_id,
            reactions=reactions
        ))

    return IssueInteractionResponse(comments=enriched)


def update_issue_comment(
    db: Session,
    issue_id: str,
    comment_id: str,
    comment: IssueCommentCreate
):
    db_comment = db.query(IssueComment).filter(
        IssueComment.id == comment_id,
        IssueComment.issue_id == issue_id
    ).first()
    if not db_comment:
        raise HTTPException(status_code=401, detail="Comment not found")

    db_comment.content = comment.content
    db.commit()
    db.refresh(db_comment)
    # Re-fetch minimal fields for the user
    upd_user = db.query(User.user_id, User.name, User.email, User.picture).filter(User.user_id == db_comment.created_by).first()
    return IssueCommentResponse(
        id=db_comment.id,
        content=db_comment.content,
        created_by=UserDTO(
            user_id=upd_user.user_id if upd_user else db_comment.created_by,
            name=upd_user.name if upd_user else None,
            email=upd_user.email if upd_user else None,
            picture=upd_user.picture if upd_user else None
        ),
        created_at=int(db_comment.created_at.timestamp()) if db_comment.created_at else None,
        issue_id=db_comment.issue_id
    )


def delete_issue_comment(db: Session, issue_id: str, comment_id: str):
    db_comment = db.query(IssueComment).filter(
        IssueComment.id == comment_id,
        IssueComment.issue_id == issue_id
    ).first()
    if not db_comment:
        raise HTTPException(status_code=401, detail="Comment not found")

    reply_comments = db.query(IssueComment.id).filter(
        IssueComment.parent_comment_id == comment_id
    ).all()
    reply_ids = [reply.id for reply in reply_comments]

    if reply_ids:
        db.query(CommentReaction).filter(
            CommentReaction.comment_id.in_(reply_ids)
        ).delete(synchronize_session=False)

    db.query(CommentReaction).filter(
        CommentReaction.comment_id == comment_id
    ).delete()

    db.query(IssueComment).filter(
        IssueComment.parent_comment_id == comment_id
    ).delete()

    db.delete(db_comment)
    db.commit()
    return None



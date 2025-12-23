from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.crud import issues as issues_crud
from app.schemas.issues import IssueCreate, IssueUpdate, IssueArchive, IssueUnarchive

router = APIRouter()

@router.post("", response_model=dict)
def create_issue(*, db: Session = Depends(get_db), issue: IssueCreate, current_user: dict = Depends(get_current_user)):
    """Create a new issue."""
    return issues_crud.create_issue(db=db, issue_data=issue.dict())

@router.get("")
def list_issues(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    team_id: Optional[str] = Query(None, description="Filter by team ID"),
    statuses: Optional[List[str]] = Query(None, description="Filter by statuses"),
    assignee: Optional[str] = Query(None, description="Filter by assignee"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    cycle_id: Optional[str] = Query(None, description="Filter by cycle ID"),
    include_archived: bool = Query(False, description="Include archived issues in results")
):
    """List all issues with pagination and optional filtering."""
    return issues_crud.list_issues(
        db=db, offset=offset, limit=limit, 
        team_id=team_id, statuses=statuses, 
        assignee=assignee, priority=priority, 
        cycle_id=cycle_id, include_archived=include_archived
    )

@router.get("/{issue_id}")
def get_issue(*, db: Session = Depends(get_db), issue_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific issue by ID."""
    issue = issues_crud.get_issue(db=db, issue_id=issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue

@router.patch("/{issue_id}")
def update_issue(
    *, db: Session = Depends(get_db), issue_id: str, issue: IssueUpdate, current_user: dict = Depends(get_current_user)
):
    """Update an issue."""
    return issues_crud.update_issue(db=db, issue_id=issue_id, issue_data=issue.dict(exclude_unset=True))

@router.post("/{issue_id}/archive")
def archive_issue(*, db: Session = Depends(get_db), issue_id: str, archive_data: IssueArchive, current_user: dict = Depends(get_current_user)):
    """Archive an issue instead of deleting it."""
    return issues_crud.archive_issue(
        db=db, issue_id=issue_id, 
        archived_by=archive_data.archived_by,
        reason=archive_data.reason
    )

@router.post("/{issue_id}/unarchive")
def unarchive_issue(*, db: Session = Depends(get_db), issue_id: str, unarchive_data: IssueUnarchive, current_user: dict = Depends(get_current_user)):
    """Unarchive an issue."""
    return issues_crud.unarchive_issue(
        db=db, issue_id=issue_id, 
        unarchived_by=unarchive_data.unarchived_by
    )

@router.delete("/{issue_id}")
def delete_issue(*, db: Session = Depends(get_db), issue_id: str, current_user: dict = Depends(get_current_user)):
    """Hard delete an issue - use with caution! Only for admin operations."""
    issues_crud.delete_issue(db=db, issue_id=issue_id)
    return {"message": "Issue deleted", "issue_id": issue_id}

@router.get("/{issue_id}/sub_issues")
def get_sub_issues(*, db: Session = Depends(get_db), issue_id: str, current_user: dict = Depends(get_current_user)):
    """Get all sub-issues of a specific issue."""
    return issues_crud.get_sub_issues(db=db, issue_id=issue_id)


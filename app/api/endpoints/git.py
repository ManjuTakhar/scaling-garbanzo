from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.crud import git_links as git_crud

router = APIRouter()

@router.post("/links", response_model=dict)
def create_git_link(
    *, 
    db: Session = Depends(get_db), 
    link_data: dict
):
    """Create a new git link."""
    link = git_crud.create_link(db=db, data=link_data)
    return {
        "id": link.id,
        "local_issue_id": link.local_issue_id,
        "provider": link.provider,
        "repository": link.repository,
        "github_issue_number": link.github_issue_number,
        "pr_number": link.pr_number,
        "branch_name": link.branch_name
    }

@router.get("/links/issue/{local_issue_id}", response_model=List[dict])
def get_links_for_issue(
    *, 
    db: Session = Depends(get_db), 
    local_issue_id: str
):
    """Get all git links for a local issue."""
    links = git_crud.get_links_for_local_issue(db=db, local_issue_id=local_issue_id)
    return [
        {
            "id": link.id,
            "local_issue_id": link.local_issue_id,
            "provider": link.provider,
            "repository": link.repository,
            "github_issue_number": link.github_issue_number,
            "pr_number": link.pr_number,
            "branch_name": link.branch_name
        } for link in links
    ]

@router.get("/links/issue/{local_issue_id}/repo/{repository}", response_model=dict)
def get_github_link(
    *, 
    db: Session = Depends(get_db), 
    local_issue_id: str,
    repository: str
):
    """Get a specific GitHub link."""
    link = git_crud.get_github_link(db=db, local_issue_id=local_issue_id, repository=repository)
    if not link:
        raise HTTPException(status_code=404, detail="Git link not found")
    return {
        "id": link.id,
        "local_issue_id": link.local_issue_id,
        "provider": link.provider,
        "repository": link.repository,
        "github_issue_number": link.github_issue_number,
        "pr_number": link.pr_number,
        "branch_name": link.branch_name
    }



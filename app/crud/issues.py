from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.issue import Issue as IssueModel, TeamIssueSequence
from app.models.teams import Team as TeamModel
from app.models.cycle import Cycle as CycleModel
from app.models.label import Label, IssueLabel
from app.models.user import User as UserModel
from app.dto.dtos import IssueDTO, TeamDTO, LabelDTO, UserDTO
from app.crud import labels as label_crud
from app.core.utils import generate_display_id
from sqlalchemy import func
from datetime import datetime

def get_next_sequence_number(db: Session, team_id: str) -> int:
    """Get the next sequence number for the team."""
    sequence_entry = db.query(TeamIssueSequence).filter(TeamIssueSequence.team_id == team_id).first()
    if not sequence_entry:
        sequence_entry = TeamIssueSequence(team_id=team_id, sequence_number=0)
        db.add(sequence_entry)
    
    sequence_entry.sequence_number += 1
    db.commit()
    return sequence_entry.sequence_number

def create_issue(db: Session, issue_data: dict) -> dict:
    """Create a new issue."""
    team = None
    display_id = issue_data.get('display_id')
    
    # Convert empty strings to None for optional fields
    if issue_data.get('cycle_id') == '':
        issue_data['cycle_id'] = None
    # if issue_data.get('epic_id') == '':
    #     issue_data['epic_id'] = None
    if issue_data.get('assignee') == '':
        issue_data['assignee'] = None
    
    if issue_data.get('team_id'):
        team = db.query(TeamModel).filter(TeamModel.team_id == issue_data['team_id']).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        if not display_id:
            sequence_number = get_next_sequence_number(db, issue_data['team_id'])
            display_id = generate_display_id(team.name, sequence_number)
    
    db_issue = IssueModel(
        display_id=display_id,
        title=issue_data.get('title'),
        description=issue_data.get('description'),
        acceptance_criteria=issue_data.get('acceptance_criteria'),
        status=issue_data.get('status', 'TODO'),
        priority=issue_data.get('priority', 'MEDIUM'),
        issue_type=issue_data.get('issue_type', 'FEATURE'),
        assignee=issue_data.get('assignee'),
        created_by=issue_data.get('created_by'),
        updated_by=issue_data.get('created_by'),
        # epic_id=issue_data.get('epic_id') or None,  # Commented out since Epic model doesn't exist
        story_points=issue_data.get('story_points'),
        cycle_id=issue_data.get('cycle_id') or None,
        team_id=issue_data.get('team_id'),
        start_date=datetime.fromtimestamp(issue_data['start_date']) if issue_data.get('start_date') else None,
        due_date=datetime.fromtimestamp(issue_data['due_date']) if issue_data.get('due_date') else None,
    )
    db.add(db_issue)
    db.flush()
    
    # Add labels if provided
    labels = []
    if issue_data.get('labels'):
        for label_name in issue_data['labels']:
            label_dto = label_crud.add_label_to_issue(db, db_issue.id, label_name, issue_data['created_by'])
            labels.append(label_dto)
    
    db.commit()
    db.refresh(db_issue)
    
    # Query only the needed columns to avoid schema mismatch
    assignee_user = None
    if db_issue.assignee:
        assignee_user = db.query(
            UserModel.user_id, UserModel.name, UserModel.email, UserModel.picture
        ).filter(UserModel.user_id == db_issue.assignee).first()
    
    created_by_user = db.query(
        UserModel.user_id, UserModel.name, UserModel.email, UserModel.picture
    ).filter(UserModel.user_id == db_issue.created_by).first()
    
    return issue_to_dto(db_issue, assignee_user, created_by_user, team, labels)

def get_issue(db: Session, issue_id: str, include_archived: bool = False) -> Optional[dict]:
    """Get a specific issue by ID."""
    query = db.query(IssueModel).filter(IssueModel.id == issue_id)
    if not include_archived:
        query = query.filter(IssueModel.is_archived != "true")
    
    db_issue = query.first()
    if not db_issue:
        return None
    
    team = db.query(TeamModel).filter(TeamModel.team_id == db_issue.team_id).first() if db_issue.team_id else None
    
    # Query only the needed columns to avoid schema mismatch
    assignee_user = None
    if db_issue.assignee:
        assignee_user = db.query(
            UserModel.user_id, UserModel.name, UserModel.email, UserModel.picture
        ).filter(UserModel.user_id == db_issue.assignee).first()
    
    created_by_user = db.query(
        UserModel.user_id, UserModel.name, UserModel.email, UserModel.picture
    ).filter(UserModel.user_id == db_issue.created_by).first()
    
    updated_by_user = None
    if db_issue.updated_by:
        updated_by_user = db.query(
            UserModel.user_id, UserModel.name, UserModel.email, UserModel.picture
        ).filter(UserModel.user_id == db_issue.updated_by).first()
    
    labels = []
    labels_query = db.query(Label, IssueLabel).join(IssueLabel).filter(IssueLabel.issue_id == issue_id)
    for label, issue_label in labels_query.all():
        labels.append(LabelDTO(id=label.id, name=label.name, color=label.color, description=label.description))
    
    return issue_to_dto(db_issue, assignee_user, created_by_user, team, labels, updated_by_user)

def list_issues(
    db: Session,
    offset: int = 0,
    limit: int = 100,
    team_id: Optional[str] = None,
    statuses: Optional[List[str]] = None,
    assignee: Optional[str] = None,
    priority: Optional[str] = None,
    cycle_id: Optional[str] = None,
    include_archived: bool = False
) -> List[dict]:
    """List all issues with pagination."""
    query = db.query(IssueModel)
    
    if not include_archived:
        query = query.filter(IssueModel.is_archived != "true")
    if team_id:
        query = query.filter(IssueModel.team_id == team_id)
    if statuses:
        query = query.filter(IssueModel.status.in_(statuses))
    if assignee:
        query = query.filter(IssueModel.assignee == assignee)
    if priority:
        query = query.filter(IssueModel.priority == priority)
    if cycle_id:
        query = query.filter(IssueModel.cycle_id == cycle_id)
    
    issues = query.order_by(IssueModel.created_at.desc()).offset(offset).limit(limit).all()
    
    results = []
    for issue in issues:
        # Query team separately
        team = db.query(TeamModel).filter(TeamModel.team_id == issue.team_id).first() if issue.team_id else None
        
        assignee_user = None
        if issue.assignee:
            assignee_user = db.query(
                UserModel.user_id, UserModel.name, UserModel.email, UserModel.picture
            ).filter(UserModel.user_id == issue.assignee).first()
        
        created_by_user = db.query(
            UserModel.user_id, UserModel.name, UserModel.email, UserModel.picture
        ).filter(UserModel.user_id == issue.created_by).first()
        
        labels = []
        labels_query = db.query(Label, IssueLabel).join(IssueLabel).filter(IssueLabel.issue_id == issue.id)
        for label, _ in labels_query.all():
            labels.append(LabelDTO(id=label.id, name=label.name, color=label.color, description=label.description))
        
        results.append(issue_to_dto(issue, assignee_user, created_by_user, team, labels))
    
    return results

def update_issue(db: Session, issue_id: str, issue_data: dict) -> dict:
    """Update an existing issue."""
    db_issue = db.query(IssueModel).filter(IssueModel.id == issue_id).first()
    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # Update fields
    for key, value in issue_data.items():
        if hasattr(db_issue, key) and key not in ['labels', 'id']:
            if key in ['start_date', 'due_date'] and value:
                setattr(db_issue, key, datetime.fromtimestamp(value))
            else:
                setattr(db_issue, key, value)
    
    # Update labels if provided
    if 'labels' in issue_data:
        # Remove existing labels
        db.query(IssueLabel).filter(IssueLabel.issue_id == issue_id).delete()
        # Add new labels
        for label_name in issue_data['labels']:
            label_crud.add_label_to_issue(db, issue_id, label_name, issue_data.get('updated_by', db_issue.updated_by))
    
    db.commit()
    db.refresh(db_issue)
    
    team = db.query(TeamModel).filter(TeamModel.team_id == db_issue.team_id).first() if db_issue.team_id else None
    
    assignee_user = None
    if db_issue.assignee:
        assignee_user = db.query(
            UserModel.user_id, UserModel.name, UserModel.email, UserModel.picture
        ).filter(UserModel.user_id == db_issue.assignee).first()
    
    created_by_user = db.query(
        UserModel.user_id, UserModel.name, UserModel.email, UserModel.picture
    ).filter(UserModel.user_id == db_issue.created_by).first()
    
    labels = []
    labels_query = db.query(Label, IssueLabel).join(IssueLabel).filter(IssueLabel.issue_id == issue_id)
    for label, _ in labels_query.all():
        labels.append(LabelDTO(id=label.id, name=label.name, color=label.color, description=label.description))
    
    return issue_to_dto(db_issue, assignee_user, created_by_user, team, labels)

def archive_issue(db: Session, issue_id: str, archived_by: str, reason: Optional[str] = None) -> dict:
    """Archive an issue."""
    db_issue = db.query(IssueModel).filter(IssueModel.id == issue_id).first()
    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    db_issue.is_archived = "true"
    db_issue.archived_at = datetime.now()
    db_issue.archived_by = archived_by
    db_issue.archive_reason = reason
    
    db.commit()
    db.refresh(db_issue)
    
    return get_issue(db, issue_id, include_archived=True)

def unarchive_issue(db: Session, issue_id: str, unarchived_by: str) -> dict:
    """Unarchive an issue."""
    db_issue = db.query(IssueModel).filter(IssueModel.id == issue_id).first()
    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    db_issue.is_archived = "false"
    db_issue.archived_at = None
    db_issue.archived_by = None
    db_issue.archive_reason = None
    
    db.commit()
    db.refresh(db_issue)
    
    return get_issue(db, issue_id)

def delete_issue(db: Session, issue_id: str) -> None:
    """Delete an issue."""
    db_issue = db.query(IssueModel).filter(IssueModel.id == issue_id).first()
    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # Delete related data
    db.query(IssueLabel).filter(IssueLabel.issue_id == issue_id).delete()
    
    db.delete(db_issue)
    db.commit()

def get_sub_issues(db: Session, issue_id: str) -> List[dict]:
    """Get all sub-issues of a specific issue."""
    db_issue = db.query(IssueModel).filter(IssueModel.id == issue_id).first()
    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    sub_issues = db.query(IssueModel).filter(IssueModel.parent_issue_id == issue_id).all()
    
    results = []
    for sub_issue in sub_issues:
        team = db.query(TeamModel).filter(TeamModel.team_id == sub_issue.team_id).first() if sub_issue.team_id else None
        
        assignee_user = None
        if sub_issue.assignee:
            assignee_user = db.query(
                UserModel.user_id, UserModel.name, UserModel.email, UserModel.picture
            ).filter(UserModel.user_id == sub_issue.assignee).first()
        
        created_by_user = db.query(
            UserModel.user_id, UserModel.name, UserModel.email, UserModel.picture
        ).filter(UserModel.user_id == sub_issue.created_by).first()
        
        results.append(issue_to_dto(sub_issue, assignee_user, created_by_user, team, []))
    
    return results

def issue_to_dto(issue, assignee_user, created_by_user, team, labels, updated_by_user=None):
    """Helper to convert Issue model to DTO."""
    return {
        "id": issue.id,
        "display_id": issue.display_id,
        "title": issue.title,
        "description": issue.description,
        "acceptance_criteria": issue.acceptance_criteria,
        "status": issue.status,
        "priority": issue.priority,
        "issue_type": issue.issue_type,
        "assignee": UserDTO(
            user_id=assignee_user.user_id if assignee_user else None,
            name=assignee_user.name if assignee_user else None,
            email=assignee_user.email if assignee_user else None,
            picture=assignee_user.picture if assignee_user else None
        ) if assignee_user else None,
        "created_at": int(issue.created_at.timestamp()) if issue.created_at else None,
        "updated_at": int(issue.updated_at.timestamp()) if issue.updated_at else None,
        "start_date": int(issue.start_date.timestamp()) if issue.start_date else None,
        "due_date": int(issue.due_date.timestamp()) if issue.due_date else None,
        "story_points": issue.story_points,
        "cycle_id": issue.cycle_id,
        "epic_id": None,  # Commented out since Epic model doesn't exist
        "created_by": UserDTO(
            user_id=created_by_user.user_id if created_by_user else None,
            name=created_by_user.name if created_by_user else None,
            email=created_by_user.email if created_by_user else None,
            picture=created_by_user.picture if created_by_user else None
        ) if created_by_user else None,
        "team": TeamDTO(
            team_id=team.team_id,
            name=team.name
        ) if team else None,
        "labels": labels,
        "is_archived": issue.is_archived == "true" if isinstance(issue.is_archived, str) else issue.is_archived,
    }


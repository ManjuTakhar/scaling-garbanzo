from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.label import Label, IssueLabel
from fastapi import HTTPException
import random
from app.dto.dtos import LabelDTO, UserDTO

def generate_random_color() -> str:
    """Generate a random hex color."""
    return f"#{random.randint(0, 0xFFFFFF):06x}"

def create_label(db: Session, name: str, created_by: str, 
                 color: Optional[str] = None, description: Optional[str] = None) -> LabelDTO:
    """
    Create a new label. If color is not provided, generates a random color.
    """
    # Check if label with same name exists
    db_label = db.query(Label).filter(Label.name == name).first()
    if db_label:
        return LabelDTO(
            id=db_label.id,
            name=db_label.name,
            color=db_label.color,
            description=db_label.description,
            created_by=None,  # Skip user loading to avoid schema conflicts
            created_at=int(db_label.created_at.timestamp())
        )
        
    # Create new label
    db_label = Label(
        name=name,
        color=color or generate_random_color(),
        description=description,
        created_by=created_by
    )
    
    db.add(db_label)
    db.commit()
    db.refresh(db_label)
    
    return LabelDTO(
        id=db_label.id,
        name=db_label.name,
        color=db_label.color,
        description=db_label.description,
        created_by=None,
        created_at=int(db_label.created_at.timestamp())
    )

def add_label_to_issue(db: Session, issue_id: str, label_name: str, created_by: str) -> LabelDTO:
    """
    Add a label to an issue. Creates the label if it doesn't exist.
    """
    # Get or create label (without eager loading user to avoid schema conflicts)
    db_label = db.query(Label).filter(Label.name == label_name).first()
    if not db_label:
        # Create new label
        db_label = Label(
            name=label_name,
            color=generate_random_color(),
            created_by=created_by
        )
        db.add(db_label)
        db.flush()  # Get the id without committing
    
    # Check if label is already added to issue
    existing = db.query(IssueLabel).filter(
        IssueLabel.issue_id == issue_id,
        IssueLabel.label_id == db_label.id
    ).first()
    
    if not existing:
        # Create new issue-label association
        issue_label = IssueLabel(
            issue_id=issue_id,
            label_id=db_label.id,
            created_by=created_by
        )
        db.add(issue_label)
        db.commit()
        db.refresh(db_label)
    
    return LabelDTO(
        id=db_label.id,
        name=db_label.name,
        color=db_label.color,
        description=db_label.description,
        created_by=None,  # Skip user loading to avoid schema conflicts
        created_at=int(db_label.created_at.timestamp())
    )

def get_label_by_name(db: Session, name: str) -> Optional[LabelDTO]:
    """
    Get a label by name.
    """
    db_label = db.query(Label).filter(Label.name == name).first()
    if not db_label:
        return None
    return LabelDTO(
        id=db_label.id,
        name=db_label.name,
        color=db_label.color,
        description=db_label.description,
        created_by=None,
        created_at=int(db_label.created_at.timestamp())
    )

def get_labels(db: Session, issue_id: str, skip: int = 0, limit: int = 100) -> List[LabelDTO]:
    """
    Get all labels with pagination.
    """
    query = db.query(Label)
    if issue_id:
        query = query.join(IssueLabel).filter(IssueLabel.issue_id == issue_id)
    db_labels = query.offset(skip).limit(limit).all()
    return [LabelDTO(
        id=label.id,
        name=label.name,
        color=label.color,
        description=label.description,
        created_by=None,
        created_at=int(label.created_at.timestamp())
    ) for label in db_labels]

def remove_label_from_issue(db: Session, issue_id: str, label_id: str) -> bool:
    """
    Remove a label from an issue.
    """
    result = db.query(IssueLabel).filter(
        IssueLabel.issue_id == issue_id,
        IssueLabel.label_id == label_id
    ).delete()
    
    db.commit()
    return bool(result)


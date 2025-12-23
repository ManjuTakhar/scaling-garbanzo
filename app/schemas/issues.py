from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.dto.dtos import UserDTO, TeamDTO, LabelDTO

class IssueStatus(str, Enum):
    BACKLOG = "BACKLOG"
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    IN_REVIEW = "IN_REVIEW"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class IssuePriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class IssueType(str, Enum):
    BUG = "BUG"
    IMPROVEMENT = "IMPROVEMENT"
    FEATURE = "FEATURE"

class IssueCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Issue title")
    description: Optional[Dict[str, Any]] = Field(None, description="Issue description as JSON")
    acceptance_criteria: Optional[Dict[str, Any]] = Field(None, description="Acceptance criteria as JSON")
    created_by: str = Field(..., description="User ID who created the issue")
    team_id: str = Field(..., description="Team ID for the issue")
    status: IssueStatus = Field(IssueStatus.TODO, description="Issue status")
    priority: IssuePriority = Field(IssuePriority.MEDIUM, description="Issue priority")
    issue_type: IssueType = Field(IssueType.FEATURE, description="Type of issue")
    assignee: Optional[str] = Field(None, description="User ID of assignee")
    start_date: Optional[int] = Field(None, description="Start date as Unix timestamp")
    due_date: Optional[int] = Field(None, description="Due date as Unix timestamp")
    story_points: Optional[int] = Field(None, description="Story points estimation")
    cycle_id: Optional[str] = Field(None, description="Cycle/Sprint ID")
    epic_id: Optional[str] = Field(None, description="Epic ID")
    labels: Optional[List[str]] = Field(None, description="List of label names to add")

class IssueUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[Dict[str, Any]] = None
    acceptance_criteria: Optional[Dict[str, Any]] = None
    status: Optional[IssueStatus] = None
    priority: Optional[IssuePriority] = None
    issue_type: Optional[IssueType] = None
    assignee: Optional[str] = None
    start_date: Optional[int] = None
    due_date: Optional[int] = None
    story_points: Optional[int] = None
    cycle_id: Optional[str] = None
    epic_id: Optional[str] = None
    team_id: Optional[str] = None
    labels: Optional[List[str]] = None
    updated_by: Optional[str] = None

class IssueArchive(BaseModel):
    reason: Optional[str] = Field(None, max_length=500, description="Reason for archiving")
    archived_by: str = Field(..., description="User ID who is archiving")

class IssueUnarchive(BaseModel):
    unarchived_by: str = Field(..., description="User ID who is unarchiving")



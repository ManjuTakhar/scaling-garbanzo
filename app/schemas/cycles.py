from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class CycleStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    UPCOMING = "UPCOMING"

class CycleCreate(BaseModel):
    name: str = Field(..., description="Cycle name")
    start_date: int = Field(..., description="Start date as Unix timestamp")
    due_date: int = Field(..., description="Due date as Unix timestamp")
    created_by: str = Field(..., description="User ID who created the cycle")
    team_id: str = Field(..., description="Team ID")
    description: Optional[str] = Field(None, description="Cycle description")

class CycleUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Cycle name")
    start_date: Optional[int] = Field(None, description="Start date as Unix timestamp")
    due_date: Optional[int] = Field(None, description="Due date as Unix timestamp")
    updated_by: Optional[str] = Field(None, description="User ID who updated")
    status: Optional[str] = Field(None, description="Cycle status")
    description: Optional[str] = Field(None, description="Cycle description")


class StartCycleRequest(BaseModel):
    started_by: str = Field(..., description="User ID who is starting the cycle")


class CompleteCycleRequest(BaseModel):
    completed_by: str = Field(..., description="User ID who completes the cycle")
    issues_to_move: Optional[List[str]] = Field(None, description="Issue IDs to move explicitly")
    move_to_backlog: Optional[bool] = Field(False, description="Move remaining issues to backlog")
    new_cycle_id: Optional[str] = Field(None, description="Target cycle to move issues to")


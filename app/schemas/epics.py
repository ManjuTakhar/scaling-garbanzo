from typing import Optional
from pydantic import BaseModel, Field

class EpicCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Epic title")
    description: str = Field(..., description="Epic description")
    status: str = Field(default="TODO", description="Epic status")
    start_date: Optional[int] = Field(None, description="Start date as Unix timestamp")
    due_date: Optional[int] = Field(None, description="Due date as Unix timestamp")
    story_points: Optional[int] = Field(None, description="Story points estimation")
    sprint_id: Optional[str] = Field(None, description="Sprint ID")
    created_by: str = Field(..., description="User ID who created the epic")

class EpicUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[int] = None
    due_date: Optional[int] = None
    story_points: Optional[int] = None
    sprint_id: Optional[str] = None
    updated_by: Optional[str] = None



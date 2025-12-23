from pydantic import BaseModel, Field
from typing import Dict, Any

class CycleUpdateCreate(BaseModel):
    created_by: str = Field(..., description="User ID who created the update")
    content: Dict[str, Any] = Field(..., description="Update content as JSON")

class CycleUpdateUpdate(BaseModel):
    updated_by: str = Field(..., description="User ID who updated")
    content: Dict[str, Any] = Field(..., description="Updated content as JSON")



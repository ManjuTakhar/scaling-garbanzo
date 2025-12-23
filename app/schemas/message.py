from pydantic import BaseModel
from typing import List, Optional

class Attachment(BaseModel):
    title: str
    text: str
    color: Optional[str] = None  # Optional field for color

class Message(BaseModel):
    channel: str
    text: str
    attachments: Optional[List[Attachment]] = None  # List of attachments 
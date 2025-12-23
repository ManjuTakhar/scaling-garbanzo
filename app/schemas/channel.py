from pydantic import BaseModel
from typing import Optional, List


class ChannelSchema(BaseModel):
    channel_id: str
    name: str 
    is_channel: Optional[bool] = None
    is_private: Optional[bool] = None
    created: Optional[int] = None
    is_archived: Optional[bool] = None
    is_general: Optional[bool] = None
    creator: Optional[str] = None
    purpose: Optional[str] = None
    topic: Optional[str] = None
    num_members: Optional[int] = None
    team_id: Optional[str] = None
    workspace_id: str

class ChannelResponse(ChannelSchema):
    pass
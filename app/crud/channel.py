from sqlalchemy.orm import Session
from app.models.channel import Channel
from app.schemas.channel import ChannelSchema, ChannelResponse
from typing import List

def add_channel(db: Session, channel_data: ChannelSchema) -> ChannelResponse:
    channel = Channel(
        channel_id=channel_data.channel_id,
        name=channel_data.name,
        is_channel=channel_data.is_channel,
        is_private=channel_data.is_private,
        created=channel_data.created,
        is_archived=channel_data.is_archived,
        is_general=channel_data.is_general,
        creator=channel_data.creator,
        purpose=channel_data.purpose,
        topic=channel_data.topic,
        num_members=channel_data.num_members,
        team_id=channel_data.team_id,
        workspace_id=channel_data.workspace_id
    )
    db.add(channel)
    db.commit()
    return channel 

def get_channel_by_id(db: Session, channel_id: str) -> ChannelResponse:
    channel = db.query(Channel).filter(Channel.channel_id == channel_id).first()
    return channel if channel else None

def get_channels_by_workspace_id(db: Session, workspace_id: str) -> List[ChannelResponse]:
    """Fetch all channels for a specific workspace."""
    channels = db.query(Channel).filter(Channel.workspace_id == workspace_id).all()
    return [ChannelResponse(**channel.__dict__) for channel in channels]
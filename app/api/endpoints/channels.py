from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.crud.channel import get_channels_by_workspace_id  # Fetch channels by workspace
from app.schemas.channel import ChannelResponse
from app.services.slack_service import SlackService
from app.schemas.message import Message  # Import the Message model
from app.api.dependencies import get_current_user
from app.crud import user as user_crud

from typing import List, Dict

router = APIRouter()

@router.get("/channels/{workspace_id}", response_model=List[ChannelResponse])
def get_all_channels(workspace_id: str, 
                     db: Session = Depends(get_db),
                     current_user: dict = Depends(get_current_user)):
    """API endpoint to fetch all channels for a specific workspace."""
    user = user_crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated, please login")
    channels = get_channels_by_workspace_id(db, workspace_id)
    if not channels:
        raise HTTPException(status_code=404, detail="No channels found for this workspace.")
    return channels 

# @router.post("/channels/{channel_id}/message")
# async def post_message(channel_id: str, 
#                        db: Session = Depends(get_db), 
#                        current_user: dict = Depends(get_current_user),
#                        message: Message = Body(...)):  # Use the Message model
#     """API endpoint to post a message to a specific channel."""
#     user = user_crud.get_user_by_email(db, current_user["email"])
#     if not user:
#         raise HTTPException(status_code=401, detail="User not authenticated, please login")
#     slack_service = SlackService(db=db)  # Initialize your Slack service

#     tenant_id = 'STR-SYN-72054778'

#     # Extract the message text and channel from the request body
#     message_text = message.text
#     channel_id = message.channel  # Use the channel from the message model

#     if not message_text:
#         raise HTTPException(status_code=400, detail="Message text is required.")

#     # Post the message to the specified channel
#     try:
#         response = await slack_service.post_message_to_channel(tenant_id, channel_id, message.dict())
#         return {"message": "Message posted successfully", "response": response}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
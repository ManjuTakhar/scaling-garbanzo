import requests
from fastapi import HTTPException
from app.core.config import settings
from app.crud import channel as channel_crud
from app.schemas.channel import ChannelResponse
from cryptography.fernet import Fernet
from app.crud import tenant as tenant_crud
from sqlalchemy.orm import Session
from app.schemas.channel import ChannelSchema
import httpx
from app.transformers.ui_update_to_slack_message import UIUpdateToSlackMessage

class SlackService:

    def __init__(self, db: Session):
        self.db = db
        self.cipher_suite = Fernet(settings.FERNET_KEY)
    
    def encrypt_slack_token(self, token: str) -> str:
        """Encrypt the Slack bot token."""
        if not token:
            raise ValueError("Token cannot be empty.")
        
        # Ensure the token is encoded to bytes before encryption
        encrypted_token = self.cipher_suite.encrypt(token.encode('utf-8'))  # Encode to bytes
        return encrypted_token.decode('utf-8')  # Return as a string

    def decrypt_slack_token(self, encrypted_token: str) -> str:
        """Decrypt the Slack bot token."""
        if not encrypted_token:
            raise ValueError("Encrypted token cannot be empty.")
        
        # Decrypt the token and return as a string
        decrypted_token = self.cipher_suite.decrypt(encrypted_token.encode('utf-8'))  # Decode to bytes
        return decrypted_token.decode('utf-8')  # Return as a string

    def refresh_channels(self, tenant_id, authorization = None):
        # Get the encrypted Slack bot token for the tenant
        encrypted_token = tenant_crud.get_encrypted_slack_token_for_tenant(self.db, tenant_id)

        print(f"Encrypted token: {encrypted_token}")

        # Check if the token is empty
        if not encrypted_token:
            # Extract the token from the authorization header
            token = authorization.split(" ")[1]  # Slack bot token from the header

            print(f"Token: {token}")
            # Encrypt the token
            encrypted_token = self.encrypt_slack_token(token)  # Implement this method to encrypt the token
            print(f"Encrypted token: {encrypted_token}")
            # Save the encrypted token to the database
            if not tenant_crud.add_slack_token(self.db, tenant_id, encrypted_token):
                raise HTTPException(status_code=400, detail="Tenant not found.")

        # Decrypt the token for use
        slack_token = self.decrypt_slack_token(encrypted_token)
        print(f"Slack token: {slack_token}")

        headers = {
            "Authorization": f"Bearer {slack_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(settings.SLACK_API_URL + "conversations.list", headers=headers)
        print(f"Response: {response}")

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching channels from Slack")
        
        data = response.json()
        
        if not data.get("ok"):
            raise HTTPException(status_code=400, detail=data.get("error", "Unknown error") + f" Response: {data}")
        
        channels = data.get("channels", [])
        self.store_channels_in_db(channels, tenant_id)
        return channels 

    def store_channels_in_db(self, channels_data, tenant_id):
        for channel_data in channels_data:
            # Extract the necessary fields from the channel_data
            purpose = channel_data.get("purpose", {}).get("value", "")  # Extract purpose as a string
            topic = channel_data.get("topic", {}).get("value", "")      # Extract topic as a string

            # Check if the channel already exists in the database
            existing_channel = channel_crud.get_channel_by_id(self.db, channel_data["id"])
            
            if existing_channel:
                # Skip the channel if it already exists
                continue
            
            # Create a new channel if it doesn't exist
            channel_schema = ChannelSchema(
                channel_id=channel_data["id"],
                name=channel_data["name"],
                is_channel=channel_data["is_channel"],
                is_private=channel_data["is_private"],
                created=channel_data["created"],
                creator=channel_data["creator"],
                purpose=purpose,
                topic=topic,
                num_members=channel_data.get("num_members", 0),
                tenant_id=tenant_id
            )
            channel_crud.add_channel(self.db, channel_schema)


    async def post_message_to_channel(self, tenant_id: str, channel_id: str, message_data: dict):
        transformer = UIUpdateToSlackMessage()
        blocks = transformer.transform(message_data)

        encrypted_token = tenant_crud.get_encrypted_slack_token_for_tenant(self.db, tenant_id)
        if not encrypted_token:
            raise ValueError("No Slack token available for this tenant.")

        slack_token = self.decrypt_slack_token(encrypted_token)
        headers = {
            "Authorization": f"Bearer {slack_token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            # Post the message directly without joining the channel
            payload = {
                "channel": channel_id,
                "blocks": blocks,
                "text": "New update posted"
            }

            response = await client.post(
                "https://slack.com/api/chat.postMessage",
                headers=headers,
                json=payload
            )

            response_data = response.json()
            print(f"Post message response: {response_data}")  # Log the response

            if not response_data.get("ok"):
                error_msg = response_data.get("error", "Unknown error")
                raise Exception(f"Error posting message: {error_msg}")

            return response_data

from typing import Dict, Any, List
from slack_sdk.models.blocks import (
    SectionBlock,
    MarkdownTextObject,
    DividerBlock,
    HeaderBlock
)

class UIUpdateToSlackMessage:
    def transform(self, message_data: dict) -> list:
        content = message_data.get("content", {})
        metadata = message_data.get("metadata", {})
        
        blocks = []
        
        # Handle project and initiative updates differently
        update_type = metadata.get('update_type')
        if update_type == 'project':
            header_text = self._create_project_header(metadata)
        elif update_type == 'initiative':
            header_text = self._create_initiative_header(metadata)
        else:
            header_text = "Update"  # fallback
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": header_text
            }
        })
        
        # Add content blocks
        content_blocks = self._transform_content(content)
        blocks.extend(content_blocks)
        
        # Add metadata footer based on type
        if update_type == 'project':
            footer_elements = self._create_project_footer(metadata)
        elif update_type == 'initiative':
            footer_elements = self._create_initiative_footer(metadata)
        else:
            footer_elements = [{"type": "mrkdwn", "text": "Updated"}]
        
        blocks.append({
            "type": "context",
            "elements": footer_elements
        })
        
        # Add divider
        blocks.append({"type": "divider"})
        
        return blocks

    def _create_project_header(self, metadata: dict) -> str:
        project_name = metadata.get('project_name', 'Project')
        project_url = metadata.get('project_url', '')
        header_text = f"*<{project_url}|{project_name}> Project Update*"
        
        if metadata.get('status'):
            status_emoji = self._get_status_emoji(metadata['status'])
            header_text += f" • Status: {status_emoji} {metadata['status'].replace('_', ' ').title()}"
        
        return header_text

    def _create_initiative_header(self, metadata: dict) -> str:
        initiative_name = metadata.get('name', 'Initiative')
        initiative_url = metadata.get('url', '')
        header_text = f"*<{initiative_url}|{initiative_name}> Initiative Update*"
        
        if metadata.get('status'):
            status_emoji = self._get_status_emoji(metadata['status'])
            header_text += f" • Status: {status_emoji} {metadata['status'].replace('_', ' ').title()}"
        
        return header_text

    def _create_project_footer(self, metadata: dict) -> list:
        return [
            {
                "type": "mrkdwn",
                "text": f"Updated by {metadata.get('updated_by', 'Unknown')}"
            },
            {
                "type": "mrkdwn",
                "text": f"• <{metadata.get('project_url', '')}|View Project>"
            }
        ]

    def _create_initiative_footer(self, metadata: dict) -> list:
        return [
            {
                "type": "mrkdwn",
                "text": f"Updated by {metadata.get('updated_by', 'Unknown')}"
            },
            {
                "type": "mrkdwn",
                "text": f"• <{metadata.get('url', '')}|View Initiative>"
            }
        ]

    def _get_status_emoji(self, status: str) -> str:
        status_emojis = {
            "on_track": "✅",
            "at_risk": "⚠️",
            "blocked": "🛑",
            "completed": "🎉",
            "not_started": "⭕",
            "in_progress": "🔄"
        }
        return status_emojis.get(status.lower(), "📝")

    def _transform_content(self, content: dict) -> list:
        blocks = []
        if not content:
            return blocks

        # Transform the content based on its structure
        if "type" in content and content["type"] == "doc":
            for item in content.get("content", []):
                if item["type"] == "bulletList":
                    bullet_points = []
                    for bullet in item.get("content", []):
                        if bullet["type"] == "listItem":
                            text = self._extract_text_from_content(bullet.get("content", []))
                            if text:
                                bullet_points.append(f"• {text}")
                    
                    if bullet_points:
                        blocks.append({
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "\n".join(bullet_points)
                            }
                        })

        return blocks

    def _extract_text_from_content(self, content: list) -> str:
        text_parts = []
        for item in content:
            if item["type"] == "paragraph":
                for text_item in item.get("content", []):
                    if text_item["type"] == "text":
                        text = text_item["text"]
                        if "marks" in text_item:
                            for mark in text_item["marks"]:
                                if mark["type"] == "bold":
                                    text = f"*{text}*"
                        text_parts.append(text)
        return " ".join(text_parts) 
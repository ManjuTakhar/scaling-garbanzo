from pydantic import BaseModel, EmailStr
from typing import List, Optional
from enum import Enum

class UsageType(str, Enum):
    INDIVIDUAL = "individual"
    ORGANIZATION = "organization"

# Team Member Invite
class TeamMemberInvite(BaseModel):
    email: EmailStr
    name: Optional[str] = None

# Complete Onboarding Request Schema
class OnboardingRequest(BaseModel):
    """Complete onboarding schema - creates tenant, workspace, and invites team members"""
    usage_type: UsageType
    workspace_name: str
    team_members: Optional[List[TeamMemberInvite]] = []

# Onboarding Response
class OnboardingResponse(BaseModel):
    success: bool
    tenant_id: str
    workspace_id: str
    workspace_name: str
    usage_type: UsageType
    team_members_invited: int
    message: str

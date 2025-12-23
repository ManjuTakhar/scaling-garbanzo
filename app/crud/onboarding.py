from sqlalchemy.orm import Session
from app.schemas.onboarding import OnboardingRequest, OnboardingResponse, UsageType
from app.schemas.tenant import TenantCreate
from app.schemas.workspace import WorkspaceCreate
from app.schemas.user import UserCreate
from app.crud.tenant import create_tenant
from app.crud.workspace import create_workspace
from app.crud.user import create_user
from app.models.workspace import WorkspaceMember
from typing import List
from datetime import datetime
from app.models.user import User

def process_onboarding(db: Session, user_id: str, onboarding_data: OnboardingRequest) -> OnboardingResponse:
    """Process complete onboarding - create tenant, workspace, and invite team members."""
    
    # 1. Create new tenant
    tenant_data = TenantCreate(name=onboarding_data.workspace_name)
    tenant = create_tenant(db, tenant_data)
    
    # 2. Create workspace within the tenant
    workspace_data = WorkspaceCreate(
        name=onboarding_data.workspace_name,
        description=f"{onboarding_data.usage_type.value.title()} workspace"
    )
    workspace = create_workspace(db, workspace_data, tenant.tenant_id, user_id)
    
    # 3. Update the current user to belong to the new tenant and workspace
    # Fetch ORM User and update tenant and workspace
    current_user = db.query(User).filter(User.user_id == user_id).first()
    if current_user:
        current_user.tenant_id = tenant.tenant_id
        # Ensure the creator's selected workspace is the one just created
        current_user.workspace_id = workspace.workspace_id
        db.commit()
    
    # 4. Add workspace memberships and create team member accounts
    invited_users = []
    for member in onboarding_data.team_members:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == member.email).first()
        if not existing_user:
            # Create new user
            user_data = UserCreate(
                email=member.email,
                name=member.name or member.email.split('@')[0],
                tenant_id=tenant.tenant_id,
                role="Member",
                # Set workspace_id for the invited user to the newly created workspace
                workspace_id=workspace.workspace_id
            )
            new_user = create_user(db, user_data)
            invited_users.append(new_user)
            # Add to workspace as Member (avoid duplicates)
            existing_membership = db.query(WorkspaceMember).filter(
                WorkspaceMember.workspace_id == workspace.workspace_id,
                WorkspaceMember.user_id == new_user.user_id
            ).first()
            if not existing_membership:
                db.add(WorkspaceMember(workspace_id=workspace.workspace_id, user_id=new_user.user_id, role="Member"))
        else:
            # Update existing user's tenant
            existing_user.tenant_id = tenant.tenant_id
            # Move/assign user's active workspace to the new workspace
            existing_user.workspace_id = workspace.workspace_id
            db.commit()
            invited_users.append(existing_user)
            # Add to workspace as Member (avoid duplicates)
            existing_membership = db.query(WorkspaceMember).filter(
                WorkspaceMember.workspace_id == workspace.workspace_id,
                WorkspaceMember.user_id == existing_user.user_id
            ).first()
            if not existing_membership:
                db.add(WorkspaceMember(workspace_id=workspace.workspace_id, user_id=existing_user.user_id, role="Member"))

    # Add creator as Owner of workspace (avoid duplicate)
    owner_membership = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace.workspace_id,
        WorkspaceMember.user_id == user_id
    ).first()
    if not owner_membership:
        db.add(WorkspaceMember(workspace_id=workspace.workspace_id, user_id=user_id, role="Owner"))
    
    db.commit()
    
    # 5. Return success response
    return OnboardingResponse(
        success=True,
        tenant_id=tenant.tenant_id,
        workspace_id=workspace.workspace_id,
        workspace_name=onboarding_data.workspace_name,
        usage_type=onboarding_data.usage_type,
        team_members_invited=len(invited_users),
        message="Your workspace has been created successfully!"
    )
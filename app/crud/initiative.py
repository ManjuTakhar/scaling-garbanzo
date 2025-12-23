from sqlalchemy.orm import Session
from app.models.initiative import Initiative
from app.schemas.initiative import InitiativeCreate, InitiativeResponse, InitiativeUpdate
from datetime import datetime
from app.models.user import User  # Import User model
from app.models.teams import Team  # Import Team model
from app.models.workspace import Workspace  # Import Workspace model
from fastapi import HTTPException
from datetime import datetime
from app.dto.dtos import UserDTO, TeamDTO, ChannelDTO
from typing import List, Optional
from sqlalchemy import and_
from app.models.channel import Channel 
from app.models.updates import InitiativeUpdate
from app.dto.dtos import InitiativeUpdateDTO
from app.crud.health import get_initiative_health_summary
from app.models.initiative_teams import initiative_teams  # Import the association table

def get_initiative(db: Session, initiative_id: str) -> InitiativeResponse:
    """Fetch a single initiative by ID."""
    initiative = db.query(Initiative).filter(Initiative.initiative_id == initiative_id).first()
    if not initiative:
        raise HTTPException(status_code=401, detail="Initiative not found")

    dri_ids = [project.dri_id for project in initiative.projects if project.dri_id]
    contributors = db.query(User).filter(User.user_id.in_(dri_ids)).all()

    latest_update = db.query(InitiativeUpdate).filter(InitiativeUpdate.initiative_id == initiative_id).order_by(InitiativeUpdate.created_at.desc()).first()
    
    initiative_health = get_initiative_health_summary(db, initiative_id)

    return InitiativeResponse(
        initiative_id=str(initiative.initiative_id),
        title=initiative.title,
        short_description=initiative.short_description,
        description=initiative.description,
        priority=initiative.priority,
        owner=(
            UserDTO(
                user_id=initiative.owner.user_id,
                name=initiative.owner.name,
                email=initiative.owner.email,
                role=initiative.owner.role,
                picture=initiative.owner.picture,
            ) if initiative.owner else None
        ),
        channels=[ChannelDTO(  # Convert channels to ChannelResponse
            channel_id=channel.channel_id,
            name=channel.name,
        ) for channel in initiative.channels] if initiative.channels else [],
        teams=[TeamDTO(  # Convert teams to TeamResponse
            team_id=team.team_id,
            name=team.name,
        ) for team in initiative.teams],  # Assuming teams are accessible through the initiative
        contributors=[UserDTO(
            user_id=contributor.user_id,
            name=contributor.name,
            email=contributor.email,
            role=contributor.role,
            picture=contributor.picture,
        ) for contributor in contributors] if contributors else [],
        latest_update=InitiativeUpdateDTO(
            update_id=latest_update.update_id,
            created_at=int(latest_update.created_at.timestamp()) if latest_update.created_at else None,
            content=latest_update.content,
            current_status=latest_update.current_status
        ) if latest_update else None,
        health=initiative_health,
        status=initiative.status,
        progress=initiative.progress,
        start_date=int(initiative.start_date.timestamp()) if initiative.start_date else None,
        end_date=int(initiative.end_date.timestamp()) if initiative.end_date else None,
        workspace_id=initiative.workspace_id,
        created_at=int(initiative.created_at.timestamp()),
        last_updated=int(initiative.last_updated.timestamp()) if initiative.last_updated else None
    )

def get_all_initiatives(db: Session, teams: Optional[List[str]] = None, owners: Optional[List[str]] = None, status: Optional[str] = None, workspace_id: Optional[str] = None, member_id: Optional[str] = None):
    """Fetch all initiatives, optionally filtered by team IDs, owner IDs, status, workspace, workspace, and member visibility.

    If member_id is provided, return initiatives where the member is the owner or belongs to any associated team.
    """
    query = db.query(Initiative)

    # Apply workspace filter (required for data isolation)
    if workspace_id:
        query = query.filter(Initiative.workspace_id == workspace_id)
    else:
        # If no workspace_id provided, return empty list for security
        return []

    # If we need to filter by workspace, or member visibility, join the Team relation once.
    # For explicit team filters, also join, as we must constrain to those teams.
    if workspace_id or teams or member_id:
        query = query.join(Initiative.teams)
        if workspace_id:
            query = query.filter(Team.workspace_id == workspace_id)

    # Apply filters if provided
    if teams:
        query = query.filter(Team.team_id.in_(teams))

    # If member_id provided, include initiatives where:
    # 1. Member belongs to any associated team, OR
    # 2. Member's teammates are owners of the initiative
    if member_id:
        from app.models.teams import TeamMember
        from sqlalchemy import or_
        
        # Get all teams the member belongs to
        member_teams = db.query(TeamMember.team_id).filter(TeamMember.user_id == member_id).subquery()
        
        # Get all teammates of the member
        teammate_ids = db.query(TeamMember.user_id).join(member_teams, TeamMember.team_id == member_teams.c.team_id).subquery()
        
        # Filter by: member is in initiative team OR teammate is the owner
        query = query.filter(
            or_(
                # Member belongs to initiative team
                Team.team_id.in_(db.query(member_teams.c.team_id)),
                # Teammate is the owner
                Initiative.owner_id.in_(db.query(teammate_ids.c.user_id))
            )
        )

    if owners:
        query = query.filter(Initiative.owner_id.in_(owners))
    
    if status:
        query = query.filter(Initiative.status == status)
    
    query = query.order_by(Initiative.end_date.asc(), Initiative.last_updated.desc())

    initiatives = query.all()

    return [
        InitiativeResponse( 
            initiative_id=str(initiative.initiative_id),
            title=initiative.title,
            short_description=initiative.short_description,
            description=initiative.description,
            priority=initiative.priority,
            owner=(
                UserDTO(
                    user_id=str(initiative.owner.user_id),
                    name=initiative.owner.name,
                    email=initiative.owner.email,
                    role=initiative.owner.role,
                    picture=initiative.owner.picture,
                ) if initiative.owner else None
            ),
            status=initiative.status,
            progress=initiative.progress,
            start_date=int(initiative.start_date.timestamp()) if initiative.start_date else None,
            end_date=int(initiative.end_date.timestamp()) if initiative.end_date else None,
            workspace_id=initiative.workspace_id,
            created_at=int(initiative.created_at.timestamp()),
            last_updated=int(initiative.last_updated.timestamp()) if initiative.last_updated else None,
            teams=[TeamDTO(
                team_id=str(team.team_id),
                name=team.name,
            ) for team in initiative.teams] if initiative.teams else [],
            channels=[ChannelDTO(
                channel_id=channel.channel_id,
                name=channel.name,
            ) for channel in initiative.channels] if initiative.channels else [],
        )
        for initiative in initiatives
    ]

def create_initiative(db: Session, initiative: InitiativeCreate) -> InitiativeResponse:
    """Create a new initiative."""
    
    # Fetch the User instance based on the provided user_id (optional during testing)
    owner = None
    if initiative.owner_id:
        owner = db.query(User).filter(User.user_id == initiative.owner_id).first()
        # If invalid owner_id provided, treat as no owner instead of erroring (testing mode)

    # Fetch the Team instances based on the provided team_ids
    requested_team_ids = initiative.teams or []
    teams = db.query(Team).filter(Team.team_id.in_(requested_team_ids)).all() if requested_team_ids else []
    
    # Fetch the Channel instances based on the provided channel_ids
    requested_channel_ids = initiative.channels or []
    channels = db.query(Channel).filter(Channel.channel_id.in_(requested_channel_ids)).all() if requested_channel_ids else []
    
    # Check if all teams exist
    if len(teams) != len(requested_team_ids):
        raise ValueError("One or more teams not found")  # Handle the case where teams are not found

    # Check if all channels exist
    if len(channels) != len(requested_channel_ids):
        raise ValueError("One or more channels not found")  # Handle the case where channels are not found

    # Resolve workspace_id from workspace_id to satisfy FK and enforce isolation
    resolved_workspace_id: Optional[str] = None
    if initiative.workspace_id:
        # Get workspace_id from workspace
        workspace = db.query(Workspace).filter(Workspace.workspace_id == initiative.workspace_id).first()
        if workspace:
            resolved_workspace_id = workspace.workspace_id
        else:
            raise HTTPException(status_code=400, detail="Workspace not found")
    elif owner and owner.workspace_id:
        resolved_workspace_id = owner.workspace_id
    elif teams:
        # Fallback to the first team's workspace_id (all teams should be same workspace)
        resolved_workspace_id = teams[0].workspace_id
    else:
        # As a safety, if neither provided, reject to avoid bad workspace assignment
        raise HTTPException(status_code=400, detail="Cannot determine workspace for initiative. Provide workspace_id, owner_id, or teams.")

    db_initiative = Initiative(
        title=initiative.title,
        short_description=initiative.short_description,
        description=initiative.description,
        priority=initiative.priority,
        owner_id=owner.user_id if owner else None,  # Use the user_id from the User instance
        status=initiative.status,
        progress=initiative.progress,
        start_date=datetime.fromtimestamp(initiative.start_date) if initiative.start_date else None,  # Convert to datetime
        end_date=datetime.fromtimestamp(initiative.end_date) if initiative.end_date else None,        # Convert to datetime
        workspace_id=resolved_workspace_id,
        teams=teams,  # Associate the fetched teams
        channels=channels  # Associate the fetched channels
    )
    
    db.add(db_initiative)
    db.commit()
    db.refresh(db_initiative)

    return InitiativeResponse(
        initiative_id=str(db_initiative.initiative_id),
        title=db_initiative.title,
        short_description=db_initiative.short_description,
        description=db_initiative.description,
        priority=db_initiative.priority,
        owner=UserDTO(
            user_id=owner.user_id,
            name=owner.name,
            email=owner.email,
            role=owner.role,
            picture=owner.picture,
        ) if owner else None,
        teams=[TeamDTO(  
            team_id=team.team_id,
            name=team.name
        ) for team in db_initiative.teams] if db_initiative.teams else [],
        channels=[ChannelDTO(
            channel_id=channel.channel_id,
            name=channel.name,
        ) for channel in db_initiative.channels] if db_initiative.channels else [],
        status=db_initiative.status,
        progress=db_initiative.progress,
        start_date=int(db_initiative.start_date.timestamp()) if db_initiative.start_date else None,
        end_date=int(db_initiative.end_date.timestamp()) if db_initiative.end_date else None,
        workspace_id=db_initiative.workspace_id,
        created_at=int(db_initiative.created_at.timestamp()),
        last_updated=int(db_initiative.last_updated.timestamp()) if db_initiative.last_updated else None
    )

def update_initiative(db: Session, initiative_id: str, initiative: InitiativeUpdate) -> InitiativeResponse:
    """Update an existing initiative."""
    db_initiative = db.query(Initiative).filter(Initiative.initiative_id == initiative_id).first()
    if not db_initiative:
        raise HTTPException(status_code=401, detail="Initiative not found")  # Handle the case where the initiative is not found

    owner = None
    # Fetch the User instance based on the provided user_id
    if initiative.owner_id:
        owner = db.query(User).filter(User.user_id == initiative.owner_id).first()
        if not owner:
            raise HTTPException(status_code=401, detail="Owner not found")  # Handle the case where the user is not found
        db_initiative.owner_id = owner.user_id  # Update owner_id

    # Fetch the Team instances based on the provided team_ids
    if initiative.teams:
        teams = db.query(Team).filter(Team.team_id.in_([team for team in initiative.teams])).all()
        # Check if all teams exist
        if len(teams) != len(initiative.teams):
            raise HTTPException(status_code=401, detail="One or more teams not found")  # Handle the case where teams are not found
        db_initiative.teams = teams  # Update teams

    # Fetch the Channel instances based on the provided channel_ids
    if initiative.channels:
        channels = db.query(Channel).filter(Channel.channel_id.in_(initiative.channels)).all() 
        if len(channels) != len(initiative.channels):
            raise HTTPException(status_code=401, detail="One or more channels not found")  # Handle the case where channels are not found
        db_initiative.channels = channels  # Update channels

    # Fetch the Contributor instances based on the provided contributor_ids
    
    dri_ids = [project.dri_id for project in db_initiative.projects if project.dri_id]
    contributors = db.query(User).filter(User.user_id.in_(dri_ids)).all()

    # Update other fields
    update_data = initiative.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field not in ['owner', 'teams', 'channels']:  # Skip owner and teams as they are handled separately
            if field in ['start_date', 'end_date'] and value is not None:  # Ensure proper conversion
                try:
                    setattr(db_initiative, field, datetime.fromtimestamp(value))
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Invalid {field}: {e}")
            else:
                setattr(db_initiative, field, value)
    
    latest_update = db.query(InitiativeUpdate).filter(InitiativeUpdate.initiative_id == initiative_id).order_by(InitiativeUpdate.created_at.desc()).first()

    db.commit()
    db.refresh(db_initiative)

    return InitiativeResponse(
        initiative_id=str(db_initiative.initiative_id),
        title=db_initiative.title,
        short_description=db_initiative.short_description,
        description=db_initiative.description,
        priority=db_initiative.priority,
        owner=UserDTO( 
            user_id=db_initiative.owner_id,
            name=db_initiative.owner.name,
            email=db_initiative.owner.email,
            role=db_initiative.owner.role,
            picture=db_initiative.owner.picture,
        ) if db_initiative.owner else None,
        teams=[TeamDTO(  # Convert teams to TeamResponse
            team_id=team.team_id,
            name=team.name,
        ) for team in db_initiative.teams],
        channels=[ChannelDTO(
            channel_id=channel.channel_id,
            name=channel.name,
        ) for channel in db_initiative.channels] if db_initiative.channels else [],
        contributors=[UserDTO(
            user_id=contributor.user_id,
            name=contributor.name,
            email=contributor.email,
            role=contributor.role,
            picture=contributor.picture,
        ) for contributor in contributors] if contributors else [],
        latest_update=InitiativeUpdateDTO(
            update_id=latest_update.update_id,
            created_at=int(latest_update.created_at.timestamp()) if latest_update.created_at else None,
            content=latest_update.content,
            current_status=latest_update.current_status
        ) if latest_update else None,
        status=db_initiative.status,
        progress=db_initiative.progress,
        start_date=int(db_initiative.start_date.timestamp()) if db_initiative.start_date else None,
        end_date=int(db_initiative.end_date.timestamp()) if db_initiative.end_date else None,
        workspace_id=db_initiative.workspace_id,
        created_at=int(db_initiative.created_at.timestamp()),
        last_updated=int(db_initiative.last_updated.timestamp()) if db_initiative.last_updated else None
    )
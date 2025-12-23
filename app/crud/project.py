from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from app.models.project import Project
from app.models.user import User
from app.models.teams import Team
from app.models.workspace import Workspace  # Import Workspace model
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.schemas.user import UserResponse
from app.schemas.teams import TeamResponse
from datetime import datetime
from typing import List, Optional
from app.dto.dtos import UserDTO, TeamDTO, ChannelDTO, ProjectUpdateDTO
from app.models.channel import Channel
from app.models.updates import ProjectUpdate  # Add this import at the top of the file
from app.crud.health import get_project_health_summary

def get_project(db: Session, project_id: str) -> ProjectResponse:
    """Fetch a single project by ID."""
    project = db.query(Project).filter(Project.project_id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=401, detail="Project not found")
    
    dri_ids = [milestone.dri for milestone in project.milestones if milestone.dri]
    contributors = db.query(User).filter(User.user_id.in_(dri_ids)).all()
    
    latest_update = db.query(ProjectUpdate).filter(ProjectUpdate.project_id == project_id).order_by(ProjectUpdate.created_at.desc()).first()

    project_health = get_project_health_summary(db, project_id)

    return ProjectResponse(
        project_id=str(project.project_id),
        title=project.title,
        short_description=project.short_description,
        description=project.description,
        initiative_id=project.initiative_id,
        priority=project.priority,
        stage=project.stage,
        dri=UserDTO(
            user_id=project.dri_id,
            name=project.dri.name,
            email=project.dri.email,
            role=project.dri.role,
            picture=project.dri.picture,
        ) if project.dri else None,
        teams=[TeamDTO(
            team_id=team.team_id,
            name=team.name,
            workspace_id=team.workspace_id,
            created_at=int(team.created_at.timestamp()) if team.created_at else None
        ) for team in project.teams],
        channels=[ChannelDTO(
            channel_id=channel.channel_id,
            name=channel.name,
        ) for channel in project.channels] if project.channels else [],
        contributors=[UserDTO(
            user_id=contributor.user_id,
            name=contributor.name,
            email=contributor.email,
            role=contributor.role,
            picture=contributor.picture,
        ) for contributor in contributors] if contributors else [],
        latest_update=ProjectUpdateDTO(
            update_id=latest_update.update_id,
            created_at=int(latest_update.created_at.timestamp()) if latest_update.created_at else None,
            content=latest_update.content,
            current_status=latest_update.current_status
        ) if latest_update else None,
        health=project_health,
        status=project.status,
        progress=project.progress,
        start_date=int(project.start_date.timestamp()) if project.start_date else None,
        end_date=int(project.end_date.timestamp()) if project.end_date else None,
        workspace_id=project.workspace_id,
        created_at=int(project.created_at.timestamp()),
        last_updated=int(project.last_updated.timestamp()) if project.last_updated else None
    )

def get_projects(db: Session, dris: Optional[List[str]] = None, teams: Optional[List[str]] = None, status: Optional[str] = None, workspace_id: Optional[str] = None):
    """Get all projects and include full DRI user details"""

    query = db.query(Project)

    # Apply filters if provided
    if dris:
        query = query.filter(Project.dri_id.in_(dris)) 

    if teams:
        # Use the relationship to filter projects that have the specified teams
        query = query.join(Project.teams).filter(Team.team_id.in_(teams))

    # Filter by workspace via Team relationship if provided
    if workspace_id:
        query = query.join(Project.teams).filter(Team.workspace_id == workspace_id)

    query = query.order_by(Project.end_date.asc(), Project.last_updated.desc())

    if status:
        query = query.filter(Project.status == status)

    projects = query.all()

    return [ProjectResponse(
        project_id=str(project.project_id),
        title=project.title,
        short_description=project.short_description,
        description=project.description,
        priority=project.priority,
        stage=project.stage,
        dri=UserDTO(
            user_id=str(project.dri.user_id),
            name=project.dri.name,
            email=project.dri.email,
            role=project.dri.role,
            picture=project.dri.picture,
        ) if project.dri else None,
        teams=[TeamDTO(
            team_id=str(team.team_id),
            name=team.name,
            workspace_id=str(team.workspace_id),
            created_at=int(team.created_at.timestamp()) if team.created_at else None
        ) for team in project.teams] if project.teams else [],
        channels=[ChannelDTO(
            channel_id=channel.channel_id,
            name=channel.name,
        ) for channel in project.channels] if project.channels else [],
        status=project.status,
        initiative_id=project.initiative_id,
        progress=project.progress,
        start_date=int(project.start_date.timestamp()) if project.start_date else None,
        end_date=int(project.end_date.timestamp()) if project.end_date else None,
        workspace_id=project.workspace_id,
        created_at=int(project.created_at.timestamp()),
        last_updated=int(project.last_updated.timestamp()) if project.last_updated else None
    ) for project in projects] if projects else []

def create_project(db: Session, project: ProjectCreate) -> ProjectResponse:
    """Create a new project."""
    
    # Fetch the User instance based on the provided user_id (DRI)
    dri = db.query(User).filter(User.user_id == project.dri_id).first() if project.dri_id else None
    
    
    # Fetch the Team instances based on the provided team_ids
    teams = db.query(Team).filter(Team.team_id.in_(project.teams)).all() if project.teams else []
    
    # Check if all teams exist
    if project.teams and len(teams) != len(project.teams):
        raise ValueError("One or more teams not found")  # Handle the case where teams are not found
    
    # Fetch the Channel instances based on the provided channel_ids
    channels = db.query(Channel).filter(Channel.channel_id.in_(project.channels)).all() if project.channels else []
    # Check if all channels exist
    if project.channels and len(channels) != len(project.channels):
        raise ValueError("One or more channels not found")  # Handle the case where channels are not found

    # Resolve workspace_id from workspace_id to satisfy FK and enforce isolation
    resolved_workspace_id: Optional[str] = None
    if project.workspace_id:
        # Get workspace_id from workspace
        workspace = db.query(Workspace).filter(Workspace.workspace_id == project.workspace_id).first()
        if workspace:
            resolved_workspace_id = workspace.workspace_id
        else:
            raise HTTPException(status_code=400, detail="Workspace not found")
    elif dri and dri.workspace_id:
        resolved_workspace_id = dri.workspace_id
    elif teams:
        # Fallback to the first team's workspace_id (all teams should be same workspace)
        resolved_workspace_id = teams[0].workspace_id
    else:
        # As a safety, if neither provided, reject to avoid bad workspace assignment
        raise HTTPException(status_code=400, detail="Cannot determine workspace for project. Provide workspace_id, dri_id, or teams.")

    db_project = Project(
        title=project.title,
        short_description=project.short_description,
        description=project.description,
        priority=project.priority,
        dri_id=dri.user_id if dri else None,  # Use the user_id from the User instance
        status=project.status,
        progress=project.progress,
        start_date=datetime.fromtimestamp(project.start_date) if project.start_date else None,  # Convert to datetime
        end_date=datetime.fromtimestamp(project.end_date) if project.end_date else None,        # Convert to datetime
        workspace_id=resolved_workspace_id,
        teams=teams,  # Associate the fetched teams
        initiative_id=project.initiative_id if project.initiative_id and project.initiative_id.strip() else None,  # Convert empty string to None
        stage=project.stage,
        channels=channels  # Associate the fetched channels
    )
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    if dri:
        dri_info = UserDTO(
            user_id=dri.user_id,
            name=dri.name,
            email=dri.email,
            role=dri.role,
            picture=dri.picture,
        )
    else:
        dri_info = None

    return ProjectResponse(
        project_id=str(db_project.project_id),
        title=db_project.title,
        short_description=db_project.short_description,
        description=db_project.description,
        priority=db_project.priority,
        initiative_id=db_project.initiative_id,
        stage=db_project.stage,
        dri=dri_info,
        teams=[TeamDTO(
            team_id=team.team_id,
            name=team.name,
        ) for team in db_project.teams] if db_project.teams else [],
        channels=[ChannelDTO(
            channel_id=channel.channel_id,
            name=channel.name,
        ) for channel in db_project.channels] if db_project.channels else [],
        status=db_project.status,
        progress=db_project.progress,
        start_date=int(db_project.start_date.timestamp()) if db_project.start_date else None,
        end_date=int(db_project.end_date.timestamp()) if db_project.end_date else None,
        workspace_id=db_project.workspace_id,
        created_at=int(db_project.created_at.timestamp()),
        last_updated=int(db_project.last_updated.timestamp()) if db_project.last_updated else None
    )

def update_project(db: Session, project_id: str, project: ProjectUpdate) -> ProjectResponse:
    """Update an existing project."""
    db_project = db.query(Project).filter(Project.project_id == project_id).first()
    
    if not db_project:
        raise HTTPException(status_code=401, detail="Project not found")  # Handle the case where the project is not found

    # Fetch the User instance based on the provided user_id (DRI)
    dri = None
    if project.dri_id:
        dri = db.query(User).filter(User.user_id == project.dri_id).first()
        if not dri:
            raise HTTPException(status_code=401, detail="DRI not found")  # Handle the case where the user is not found
        db_project.dri_id = dri.user_id  # Update DRI

    # Fetch the Team instances based on the provided team_ids
    if project.teams:
        teams = db.query(Team).filter(Team.team_id.in_(project.teams)).all()
        # Check if all teams exist
        if len(teams) != len(project.teams):
            raise HTTPException(status_code=401, detail="One or more teams not found")  # Handle the case where teams are not found
        db_project.teams.clear()  # Clear existing associations
        db_project.teams.extend(teams)  # Add new teams
    
    # Fetch the Channel instances based on the provided channel_ids
    if project.channels:
        channels = db.query(Channel).filter(Channel.channel_id.in_(project.channels)).all()
        # Check if all channels exist
        if len(channels) != len(project.channels):
            raise ValueError("One or more channels not found")  # Handle the case where channels are not found
        db_project.channels.clear()  # Clear existing associations
        db_project.channels.extend(channels)  # Add new channels

    # Update other fields
    update_data = project.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field not in ['dri_id', 'teams', 'channels']:  # Skip DRI and teams as they are handled separately
            if field in ['start_date', 'end_date'] and value is not None:  # Ensure proper conversion
                try:
                    setattr(db_project, field, datetime.fromtimestamp(value))
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Invalid {field}: {e}")
            else:
                setattr(db_project, field, value)
    
    # Fetch the Contributor instances based on the provided contributor_ids
    dri_ids = [milestone.dri for milestone in db_project.milestones if milestone.dri]
    contributors = db.query(User).filter(User.user_id.in_(dri_ids)).all()

    latest_update = db.query(ProjectUpdate).filter(ProjectUpdate.project_id == project_id).order_by(ProjectUpdate.created_at.desc()).first()
    
    db.commit()
    db.refresh(db_project)

    return ProjectResponse(
        project_id=str(db_project.project_id),
        title=db_project.title,
        short_description=db_project.short_description,
        description=db_project.description,
        priority=db_project.priority,
        initiative_id=db_project.initiative_id,
        stage=db_project.stage,
        dri=UserDTO( 
            user_id=db_project.dri_id,
            name=db_project.dri.name,
            email=db_project.dri.email,
            role=db_project.dri.role,
            picture=db_project.dri.picture,
        ) if db_project.dri else None,
        teams=[TeamDTO(
            team_id=team.team_id,
            name=team.name,
        ) for team in db_project.teams] if db_project.teams else [],
        channels=[ChannelDTO(
            channel_id=channel.channel_id,
            name=channel.name,
        ) for channel in db_project.channels] if db_project.channels else [],
        contributors=[UserDTO(
            user_id=contributor.user_id,
            name=contributor.name,
            email=contributor.email,
            role=contributor.role,
            picture=contributor.picture,
        ) for contributor in contributors] if contributors else [],
        latest_update=ProjectUpdateDTO(
            update_id=latest_update.update_id,
            created_at=int(latest_update.created_at.timestamp()) if latest_update.created_at else None,
            content=latest_update.content,
            current_status=latest_update.current_status
        ) if latest_update else None,
        status=db_project.status,
        progress=db_project.progress,
        start_date=int(db_project.start_date.timestamp()) if db_project.start_date else None,
        end_date=int(db_project.end_date.timestamp()) if db_project.end_date else None,
        workspace_id=db_project.workspace_id,
        created_at=int(db_project.created_at.timestamp()),
        last_updated=int(db_project.last_updated.timestamp()) if db_project.last_updated else None
    )


def delete_project(db: Session, project_id: str) -> ProjectResponse:
    """Delete a project by ID."""
    project = db.query(Project).filter(Project.project_id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=401, detail="Project not found")

    db.delete(project)
    db.commit()

    return ProjectResponse(
        project_id=str(project.project_id),
        title=project.title,
        short_description=project.short_description,
        description=project.description,
        dri=UserDTO(
            user_id=project.dri,
            name=project.dri_user.name,
            email=project.dri_user.email,
            role=project.dri_user.role,
            picture=project.dri_user.picture,
        ),
        teams=[TeamDTO(
            team_id=team.team_id,
            name=team.name
        ) for team in project.teams] if project.teams else [],
        status=project.status,
        progress=project.progress,
        start_date=int(project.start_date.timestamp()) if project.start_date else None,
        end_date=int(project.end_date.timestamp()) if project.end_date else None,
        workspace_id=project.workspace_id,
        created_at=int(project.created_at.timestamp()),
        last_updated=int(project.last_updated.timestamp()) if project.last_updated else None
    )

def get_initiative_projects(db: Session, initiative_id: str) -> List[ProjectResponse]:
    """Get all projects for a specific initiative"""
    projects = db.query(Project).filter(Project.initiative_id == initiative_id).all()
    return [ProjectResponse(
        project_id=str(project.project_id),
        title=project.title,
        short_description=project.short_description,    
        description=project.description,
        initiative_id=project.initiative_id,
        priority=project.priority,
        stage=project.stage,
        dri=UserDTO(
            user_id=project.dri.user_id,
            name=project.dri.name,
            email=project.dri.email,
            role=project.dri.role,
            picture=project.dri.picture,
        ) if project.dri else None,
        teams=[TeamDTO(
            team_id=team.team_id,
            name=team.name
        ) for team in project.teams] if project.teams else [],
        channels=[ChannelDTO(
            channel_id=channel.channel_id,
            name=channel.name,
        ) for channel in project.channels] if project.channels else [],
        status=project.status,
        progress=project.progress,
        start_date=int(project.start_date.timestamp()) if project.start_date else None,
        end_date=int(project.end_date.timestamp()) if project.end_date else None,
        workspace_id=project.workspace_id,
        created_at=int(project.created_at.timestamp()),
        last_updated=int(project.last_updated.timestamp()) if project.last_updated else None
    ) for project in projects]

from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timedelta
from app.models.teams import Team, TeamMember
from app.models.user import User
from app.models.cycle import Cycle as CycleModel
from app.schemas.teams import (
    TeamCreate,
    TeamResponse,
    TeamMemberAdd,
    TeamMemberRemove,
    TeamMembersResponse,
    TeamMemberResponse,
    TeamUpdate,
    TeamSettingsResponse,
    TeamSettingsUpdate,
    TeamCreateWithSettings,
)
from app.schemas.user import UserResponse
from app.schemas.cycles import CycleStatus
from app.models.project import Project
from app.models.initiative import Initiative
from app.dto.dtos import ProjectDTO, InitiativeDTO, UserDTO
from app.models.initiative_teams import initiative_teams
from app.models.project_teams import project_teams
from app.crud import cycles as cycles_crud
import json

def create_team(db: Session, team: TeamCreate):
    """Create a new team and add members if provided."""
    db_team = Team(
        name=team.name,
        workspace_id=team.workspace_id,  # Use provided workspace_id
        description=team.description if team.description and team.description.strip() else None
    )
    db.add(db_team)
    db.commit()
    db.refresh(db_team)

    # If user_ids are provided, add them to the team
    if team.user_ids:
        add_team_members(db, db_team.team_id, TeamMemberAdd(user_ids=team.user_ids))

    # Return all required fields for TeamResponse
    return TeamResponse(
        team_id=db_team.team_id,
        name=db_team.name,
        description=db_team.description,
        workspace_id=db_team.workspace_id,  # Include workspace_id
        created_at=int(db_team.created_at.timestamp())  # Convert to timestamp
    )


def create_team_with_settings(db: Session, payload: TeamCreateWithSettings) -> TeamResponse:
    created = create_team(db, payload)
    db_team = db.query(Team).filter(Team.team_id == created.team_id).first()
    if db_team:
        initial = {}
        for key in ("general_settings", "issue_settings", "cycle_configuration"):
            section = getattr(payload, key, None)
            if section is not None:
                initial[key] = section
        if initial:
            db_team.settings = json.dumps(initial)
            db.commit()
            db.refresh(db_team)
            created.settings = db_team.settings
    return created

def add_team_members(db: Session, team_id: str, members: TeamMemberAdd):
    """Add multiple users to a team."""
    db_team = db.query(Team).filter(Team.team_id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=401, detail="Team not found")

    added_users = []
    for user_id in members.user_ids:
        db_user = db.query(User).filter(User.user_id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=401, detail=f"User {user_id} not found")

        existing_member = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        ).first()

        if not existing_member:
            db_team_member = TeamMember(team_id=team_id, user_id=user_id) 
            db.add(db_team_member)
            added_users.append(str(user_id))

    db.commit()
    
    # Return all required fields for TeamResponse
    return TeamResponse(
        team_id=str(db_team.team_id),
        name=db_team.name,
        description=db_team.description,
        workspace_id=db_team.workspace_id,  # Include workspace_id
        created_at=int(db_team.created_at.timestamp())  # Convert to timestamp
    )

def remove_team_members(db: Session, team_id: str, members: TeamMemberRemove):
    """Remove multiple users from a team."""
    db_team = db.query(Team).filter(Team.team_id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")

    removed_users = []
    for user_id in members.user_ids:
        # Check if user exists
        db_user = db.query(User).filter(User.user_id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")

        # Find and remove the team member relationship
        team_member = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        ).first()

        if team_member:
            db.delete(team_member)
            removed_users.append(str(user_id))

    db.commit()
    
    # Return all required fields for TeamResponse
    return TeamResponse(
        team_id=str(db_team.team_id),
        name=db_team.name,
        description=db_team.description,
        created_at=int(db_team.created_at.timestamp())  # Convert to timestamp
    )

def get_all_teams(db: Session, member_id: str | None = None, workspace_id: str | None = None):
    """Fetch teams filtered by workspace_id and optionally by member."""
    query = db.query(Team)

    # Apply workspace_id filter (required)
    if workspace_id:
        query = query.filter(Team.workspace_id == workspace_id)
    
    # If member_id provided, filter to teams the user is a member of
    if member_id:
        query = query.join(TeamMember, TeamMember.team_id == Team.team_id).filter(TeamMember.user_id == member_id)
    
    # If no member_id provided, return all teams in the workspace
    teams = query.order_by(Team.created_at.desc()).all()
    team_responses = []

    for team in teams:
        members = (
            db.query(User)
            .join(TeamMember, User.user_id == TeamMember.user_id)
            .filter(TeamMember.team_id == team.team_id)
            .all()
        )

        team_responses.append(
            TeamResponse(
                team_id=str(team.team_id),
                name=team.name,
                description=team.description,
                workspace_id=team.workspace_id,
                created_at=int(team.created_at.timestamp()),
                members=[
                    UserDTO(
                        user_id=str(user.user_id),
                        name=user.name,
                        email=user.email,
                        role=user.role,
                        picture=user.picture
                    )
                    for user in members
                ]
            )
        )

    return team_responses

def get_team_members(db: Session, team_id: str) -> TeamMembersResponse:
    """Get all users in a team with full details."""
    db_team = db.query(Team).filter(Team.team_id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=401, detail="Team not found")

    members = (
        db.query(User)
        .join(TeamMember, User.user_id == TeamMember.user_id)
        .filter(TeamMember.team_id == team_id)
        .all()
    )

    return TeamMembersResponse(
        team_id=str(db_team.team_id),
        members=[
            UserResponse(
                user_id=str(user.user_id),
                name=user.name,
                email=user.email,
                role=user.role,
                picture=user.picture,
                tenant_id=user.tenant_id,
                workspace_id=getattr(user, "workspace_id", None),
                created_at=int(user.created_at.timestamp()) if getattr(user, "created_at", None) else None,
                last_updated=int(user.last_updated.timestamp()) if getattr(user, "last_updated", None) else None
            )
            for user in members
        ]
    )

def get_team_details(db: Session, team_id: str) -> TeamResponse:
    """Get all details of a team."""
    db_team = db.query(Team).filter(Team.team_id == team_id).first()
    members = (
            db.query(User)
            .join(TeamMember, User.user_id == TeamMember.user_id)
            .filter(TeamMember.team_id == db_team.team_id)
            .all()
        )
    if not db_team:
        raise HTTPException(status_code=401, detail="Team not found")

    return TeamResponse(
        team_id=str(db_team.team_id),
        name=db_team.name,
        description=db_team.description,
        workspace_id=db_team.workspace_id,
        settings=db_team.settings,
        created_at=int(db_team.created_at.timestamp()),
        members=[
            UserDTO(
                user_id=str(user.user_id),
                name=user.name,
                email=user.email,
                role=user.role,
                picture=user.picture
            )
            for user in members 
        ]
    )


def update_team(db: Session, payload: TeamUpdate) -> TeamResponse:
    """Update basic team fields (name, description)."""
    db_team = db.query(Team).filter(Team.team_id == payload.team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    if payload.name is not None:
        db_team.name = payload.name
    if payload.description is not None:
        db_team.description = payload.description
    db.commit()
    db.refresh(db_team)

    members = (
        db.query(User)
        .join(TeamMember, User.user_id == TeamMember.user_id)
        .filter(TeamMember.team_id == payload.team_id)
        .all()
    )

    return TeamResponse(
        team_id=str(db_team.team_id),
        name=db_team.name,
        description=db_team.description,
        workspace_id=db_team.workspace_id,
        settings=db_team.settings,
        created_at=int(db_team.created_at.timestamp()),
        members=[
            UserDTO(
                user_id=str(u.user_id),
                name=u.name,
                email=u.email,
                role=u.role,
                picture=u.picture,
            )
            for u in members
        ],
    )


def get_team_settings(db: Session, team_id: str) -> TeamSettingsResponse:
    db_team = db.query(Team).filter(Team.team_id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")

    defaults = {
        "general_settings": {
            "name": db_team.name or "",
            "identifier": (db_team.team_id.split("-")[1] if db_team.team_id and "-" in db_team.team_id else "TM"),
            "status": "Active",
            "description": db_team.description or "",
        },
        "issue_settings": {
            "default_priority": "Medium",
            "default_assignee": "unassigned",
            "default_status": "To Do",
            "custom_labels": [],
        },
        "cycle_configuration": {
            "sprint_starts_with": 100,
            "cycle_name_prefix": "",
            "cycle_name_middle": "CYC",
            "sprint_duration": "2 Weeks",
            "cycle_start_day": "Monday",
            "cooldown_days": 0,
            "create_sprints_count": 2,
            "auto_start_new_cycle": False,
            "auto_carry_tasks": False,
        },
    }

    try:
        saved = json.loads(db_team.settings) if db_team.settings else {}
        for section in ("general_settings", "issue_settings", "cycle_configuration"):
            if isinstance(saved.get(section), dict):
                defaults[section].update(saved[section])
    except Exception:
        pass

    members = (
        db.query(User)
        .join(TeamMember, User.user_id == TeamMember.user_id)
        .filter(TeamMember.team_id == db_team.team_id)
        .all()
    )
    member_dicts = [
        {"id": str(u.user_id), "name": u.name, "email": u.email, "picture": u.picture, "role": getattr(u, "role", None)}
        for u in members
    ]

    return TeamSettingsResponse(
        team_id=str(db_team.team_id),
        general_settings=defaults["general_settings"],
        issue_settings=defaults["issue_settings"],
        cycle_configuration=defaults["cycle_configuration"],
        members=member_dicts,
    )


def update_team_settings(db: Session, payload: TeamSettingsUpdate) -> TeamSettingsResponse:
    db_team = db.query(Team).filter(Team.team_id == payload.team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")

    if payload.general_settings:
        name = payload.general_settings.get("name")
        desc = payload.general_settings.get("description")
        if name is not None:
            db_team.name = name
        if desc is not None:
            db_team.description = desc

    existing = {}
    try:
        existing = json.loads(db_team.settings) if db_team.settings else {}
    except Exception:
        existing = {}

    for key in ("general_settings", "issue_settings", "cycle_configuration"):
        section = getattr(payload, key)
        if section is not None:
            if key not in existing or not isinstance(existing.get(key), dict):
                existing[key] = {}
            existing[key].update(section)

    db_team.settings = json.dumps(existing)
    db.commit()
    db.refresh(db_team)

    # Create new sprints when cycle_configuration is updated
    if payload.cycle_configuration and payload.updated_by:
        cycle_config = existing.get("cycle_configuration", {})
        
        # Check if there are existing cycles for this team
        existing_cycles = db.query(CycleModel).filter(CycleModel.team_id == payload.team_id).count()
        
        # Only create sprints if there are no existing cycles
        if existing_cycles == 0:
            # Get configuration values
            sprint_starts_with = cycle_config.get("sprint_starts_with", 100)
            sprint_naming_prefix = cycle_config.get("sprint_naming_prefix", "") or cycle_config.get("cycle_name_prefix", "")
            sprint_naming_middle = cycle_config.get("sprint_naming_middle", "CYC") or cycle_config.get("cycle_name_middle", "CYC")
            sprint_duration = cycle_config.get("sprint_duration", "2 Weeks")
            cycle_start_day = cycle_config.get("cycle_start_day", "Monday")
            default_sprint_count = cycle_config.get("default_sprint_count", 2) or cycle_config.get("create_sprints_count", 2)
            
            # Calculate start date based on cycle_start_day
            today = datetime.now()
            weekdays = {
                "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                "friday": 4, "saturday": 5, "sunday": 6
            }
            target_weekday = weekdays.get(cycle_start_day.lower(), 0)
            days_ahead = target_weekday - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            start_date = today + timedelta(days=days_ahead)
            start_date = start_date.replace(hour=9, minute=0, second=0, microsecond=0)
            
            # Calculate duration in weeks
            duration_weeks = 2  # Default
            duration_text = sprint_duration.lower()
            if "1 week" in duration_text or "1week" in duration_text:
                duration_weeks = 1
            elif "3 week" in duration_text or "3week" in duration_text:
                duration_weeks = 3
            elif "4 week" in duration_text or "4week" in duration_text:
                duration_weeks = 4
            
            # Create sprints based on default_sprint_count
            for i in range(default_sprint_count or 1):
                sprint_start_date = start_date + timedelta(weeks=duration_weeks * i)
                sprint_due_date = sprint_start_date + timedelta(weeks=duration_weeks)
                
                # Calculate sprint number
                sprint_number = sprint_starts_with + i if isinstance(sprint_starts_with, int) else 100 + i
                
                # Generate sprint name
                sprint_name = f"{sprint_naming_prefix}-{sprint_naming_middle}-{sprint_number}"
                
                # Create cycle data
                cycle_data = {
                    "name": sprint_name,
                    "start_date": int(sprint_start_date.timestamp()),
                    "due_date": int(sprint_due_date.timestamp()),
                    "created_by": payload.updated_by,
                    "team_id": payload.team_id,
                    "description": f"Auto-created sprint {i+1} for team {db_team.name}",
                }
                
                try:
                    created_cycle = cycles_crud.create_cycle(db, cycle_data)
                    # Set status to UPCOMING for sprints after the first one
                    if i > 0:
                        db_cycle = db.query(CycleModel).filter(CycleModel.id == created_cycle.id).first()
                        if db_cycle:
                            db_cycle.status = CycleStatus.UPCOMING
                            db.commit()
                except Exception as e:
                    # Log error but continue creating other sprints
                    print(f"Failed to create sprint {i+1}: {str(e)}")

    return get_team_settings(db, db_team.team_id)

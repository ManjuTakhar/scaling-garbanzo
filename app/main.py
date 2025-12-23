from fastapi import FastAPI
from app.api.endpoints import initiatives, project_interactions, projects, milestones, updates, \
    resources, auth, initiative_interactions, users, teams, tenants, channels, onboarding, workspace_invitation
from app.api.endpoints import magic_link, issues  # , epics, cycles, labels, cycle_updates, git
from app.api.endpoints import cycles
from app.api.endpoints import cycle_updates
from app.api.endpoints import issue_interactions
from fastapi.middleware.cors import CORSMiddleware
from app.db.base import Base
from app.db.session import engine
from app.middleware.logging import LogRequestMiddleware
from app.models.tenant import Tenant  # Import the Tenant model
from app.models.user import User  # Import the User model
from app.models.teams import Team  # Import the Team model
from app.models.teams import TeamMember  # Import the TeamMember model
from app.models.initiative import Initiative  # Import the Initiative model
from app.models.project import Project  # Import the Project model
from app.models.initiative_teams import initiative_teams  # Import the initiative_teams table
from app.models.project_teams import project_teams  # Import the project_teams table (if applicable)
from app.models.channel import Channel  # Import the Channel model
from app.models.updates import InitiativeUpdate, ProjectUpdate  # Import the Update model
from app.models.initiative_interactions import InitiativeComment, InitiativeReaction  # Import the InitiativeComment and InitiativeReaction models
from app.models.project_interactions import ProjectComment, ProjectReaction  # Import the ProjectComment and ProjectReaction models
from app.models.project import Milestone  # Import the Milestone model
from app.models.initiative_channels import InitiativeChannel  # Import the initiative_channels table
from app.models.project_channels import ProjectChannel  # Import the project_channels table
from app.models.resource import ProjectResource, InitiativeResource  # Import the ProjectResource and InitiativeResource models
from app.models.dependencies import InitiativeDependency, ProjectDependency  # Import the InitiativeDependency and ProjectDependency models
from app.models.workspace import Workspace  # Import the Workspace model
from app.models.workspace import WorkspaceMember  # Import the WorkspaceMember model
from app.models.workspace_invitation import WorkspaceInvitation  # Import the WorkspaceInvitation model
from app.models.magic_link import MagicLink  # Import the MagicLink model
from app.api.endpoints import dependencies, health
from app.api.endpoints import workspace as workspace_endpoints
from sqlalchemy import text
app = FastAPI(title="Syncup API", description="API for Syncup project")

app.add_middleware(LogRequestMiddleware)

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    
    Base.metadata.create_all(bind=engine)

    Tenant.__table__.create(bind=engine, checkfirst=True)  # Create Tenant table
    User.__table__.create(bind=engine, checkfirst=True)  # Create User table
    Team.__table__.create(bind=engine, checkfirst=True)  # Create Team table
    TeamMember.__table__.create(bind=engine, checkfirst=True)  # Create TeamMember table
    Initiative.__table__.create(bind=engine, checkfirst=True)  # Create Initiative table
    Project.__table__.create(bind=engine, checkfirst=True)  # Create Project table
    ProjectResource.__table__.create(bind=engine, checkfirst=True)  # Create ProjectResource table
    InitiativeResource.__table__.create(bind=engine, checkfirst=True)  # Create InitiativeResource table
    initiative_teams.create(bind=engine, checkfirst=True)  # Create initiative_teams table
    project_teams.create(bind=engine, checkfirst=True)  # Create project_teams table (if applicable)
    Channel.__table__.create(bind=engine, checkfirst=True)  # Create Channel table
    InitiativeUpdate.__table__.create(bind=engine, checkfirst=True)  # Create InitiativeUpdate table
    ProjectUpdate.__table__.create(bind=engine, checkfirst=True)  # Create ProjectUpdate table
    InitiativeComment.__table__.create(bind=engine, checkfirst=True)  # Create InitiativeComment table
    InitiativeReaction.__table__.create(bind=engine, checkfirst=True)  # Create InitiativeReaction table
    ProjectComment.__table__.create(bind=engine, checkfirst=True)  # Create ProjectComment table
    ProjectReaction.__table__.create(bind=engine, checkfirst=True)  # Create ProjectReaction table
    Milestone.__table__.create(bind=engine, checkfirst=True)  # Create Milestone table
    InitiativeChannel.__table__.create(bind=engine, checkfirst=True)  # Create initiative_channels table
    ProjectChannel.__table__.create(bind=engine, checkfirst=True)  # Create project_channels table
    InitiativeDependency.__table__.create(bind=engine, checkfirst=True)  # Create InitiativeDependency table
    ProjectDependency.__table__.create(bind=engine, checkfirst=True)  # Create ProjectDependency table
    Workspace.__table__.create(bind=engine, checkfirst=True)  # Create Workspace table
    WorkspaceMember.__table__.create(bind=engine, checkfirst=True)  # Create WorkspaceMember table
    WorkspaceInvitation.__table__.create(bind=engine, checkfirst=True)  # Create WorkspaceInvitation table
    MagicLink.__table__.create(bind=engine, checkfirst=True)  # Create MagicLink table
    
    # Import and create new issue-related tables
    from app.models.issue import Issue, TeamIssueSequence
    # from app.models.epic import Epic
    from app.models.cycle import Cycle, TeamCycleSequence
    from app.models.label import Label, IssueLabel
    from app.models.issue_activity import IssueActivity
    from app.models.issue_interactions import IssueComment, CommentReaction
    from app.models.cycle_update import CycleUpdate
    from app.models.git_link import GitLink
    # from app.models.git_installation import GitInstallation
    # from app.models.otp import OTP
    
    Issue.__table__.create(bind=engine, checkfirst=True)
    TeamIssueSequence.__table__.create(bind=engine, checkfirst=True)
    # Epic.__table__.create(bind=engine, checkfirst=True)
    Cycle.__table__.create(bind=engine, checkfirst=True)
    TeamCycleSequence.__table__.create(bind=engine, checkfirst=True)
    Label.__table__.create(bind=engine, checkfirst=True)
    IssueLabel.__table__.create(bind=engine, checkfirst=True)
    IssueActivity.__table__.create(bind=engine, checkfirst=True)
    IssueComment.__table__.create(bind=engine, checkfirst=True)
    CommentReaction.__table__.create(bind=engine, checkfirst=True)
    CycleUpdate.__table__.create(bind=engine, checkfirst=True)
    GitLink.__table__.create(bind=engine, checkfirst=True)
    # GitInstallation.__table__.create(bind=engine, checkfirst=True)
    # OTP.__table__.create(bind=engine, checkfirst=True)

    # Add workspace_id column to teams table if it doesn't exist
    with engine.connect() as connection:
        try:
            connection.execute(text("ALTER TABLE teams ADD COLUMN IF NOT EXISTS workspace_id VARCHAR"))
            # Add foreign key constraint if it doesn't exist
            try:
                connection.execute(text("ALTER TABLE teams ADD CONSTRAINT fk_teams_workspace FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id)"))
            except Exception as fk_error:
                print(f"⚠️ Could not add foreign key constraint: {fk_error}")
            connection.commit()
            print("✅ Added 'workspace_id' column to 'teams' table.")
        except Exception as e:
            print(f"⚠️ Could not add 'workspace_id' column to 'teams' table: {e}")

        # Make invited_by column nullable in workspace_invitations table
        try:
            connection.execute(text("ALTER TABLE workspace_invitations ALTER COLUMN invited_by DROP NOT NULL"))
            connection.commit()
            print("✅ Made 'invited_by' column nullable in 'workspace_invitations' table.")
        except Exception as e:
            print(f"⚠️ Could not modify 'invited_by' column in 'workspace_invitations' table: {e}")

        # Ensure workspace_id columns exist on initiatives and projects
        try:
            connection.execute(text("ALTER TABLE initiatives ADD COLUMN IF NOT EXISTS workspace_id VARCHAR"))
            connection.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS workspace_id VARCHAR"))
            connection.commit()
            print("✅ Ensured 'workspace_id' columns exist on 'initiatives' and 'projects'.")
        except Exception as e:
            print(f"⚠️ Could not add 'workspace_id' columns: {e}")

        # Backfill workspace_id on initiatives via any attached team
        try:
            connection.execute(text("""
                UPDATE initiatives i
                SET workspace_id = t.workspace_id
                FROM initiative_teams it
                JOIN teams t ON t.team_id = it.team_id
                WHERE i.initiative_id = it.initiative_id
                  AND i.workspace_id IS NULL
            """))
            connection.commit()
            print("✅ Backfilled 'workspace_id' on 'initiatives' from teams.")
        except Exception as e:
            print(f"⚠️ Could not backfill 'workspace_id' on 'initiatives': {e}")

        # Backfill workspace_id on projects via any attached team
        try:
            connection.execute(text("""
                UPDATE projects p
                SET workspace_id = t.workspace_id
                FROM project_teams pt
                JOIN teams t ON t.team_id = pt.team_id
                WHERE p.project_id = pt.project_id
                  AND p.workspace_id IS NULL
            """))
            connection.commit()
            print("✅ Backfilled 'workspace_id' on 'projects' from teams.")
        except Exception as e:
            print(f"⚠️ Could not backfill 'workspace_id' on 'projects': {e}")

        # Enforce NOT NULL and add FKs
        try:
            connection.execute(text("ALTER TABLE initiatives ALTER COLUMN workspace_id SET NOT NULL"))
            connection.execute(text("ALTER TABLE projects ALTER COLUMN workspace_id SET NOT NULL"))
            # Add foreign keys (ignore if they already exist)
            try:
                connection.execute(text("ALTER TABLE initiatives ADD CONSTRAINT fk_initiatives_workspace FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id)"))
            except Exception:
                pass
            try:
                connection.execute(text("ALTER TABLE projects ADD CONSTRAINT fk_projects_workspace FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id)"))
            except Exception:
                pass
            connection.commit()
            print("✅ Enforced NOT NULL and FK constraints for 'workspace_id' on initiatives and projects.")
        except Exception as e:
            print(f"⚠️ Could not enforce NOT NULL / add FK for 'workspace_id': {e}")

        # Make initiative_id column nullable in projects table
        try:
            connection.execute(text("ALTER TABLE projects ALTER COLUMN initiative_id DROP NOT NULL"))
            connection.commit()
            print("✅ Made 'initiative_id' column nullable in 'projects' table.")
        except Exception as e:
            print(f"⚠️ Could not modify 'initiative_id' column in 'projects' table: {e}")

        # Make owner_id column nullable in initiatives table (testing: allow creating initiatives without owner)
        try:
            connection.execute(text("ALTER TABLE initiatives ALTER COLUMN owner_id DROP NOT NULL"))
            connection.commit()
            print("✅ Made 'owner_id' column nullable in 'initiatives' table.")
        except Exception as e:
            print(f"⚠️ Could not modify 'owner_id' column in 'initiatives' table: {e}")

# cors configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # NO WILDCARD when using credentials
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(channels.router, prefix="/api", tags=["channels"])
app.include_router(tenants.router, prefix="/api", tags=["tenants"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(teams.router, prefix="/api", tags=["teams"])
app.include_router(initiatives.router, prefix="/api", tags=["initiatives"])
app.include_router(projects.router, prefix="/api", tags=["projects"])
app.include_router(updates.router, prefix="/api", tags=["updates"])
app.include_router(milestones.router, prefix="/api", tags=["milestones"])
app.include_router(resources.router, prefix="/api", tags=["resources"])
app.include_router(project_interactions.router, prefix="/api", tags=["project-interactions"])
app.include_router(initiative_interactions.router, prefix="/api", tags=["initiative-interactions"])
app.include_router(dependencies.router, prefix="/api", tags=["dependencies"])
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(workspace_endpoints.router, prefix="/api", tags=["workspace"])
app.include_router(workspace_invitation.router, prefix="/api", tags=["workspace-invitations"])
app.include_router(magic_link.router, prefix="/api", tags=["magic-link"])
app.include_router(onboarding.router, prefix="/api", tags=["onboarding"])

# New issue-related endpoints
app.include_router(issues.router, prefix="/api/issues", tags=["issues"])
app.include_router(issue_interactions.router, prefix="/api", tags=["issue-interactions"])
# app.include_router(epics.router, prefix="/api/epics", tags=["epics"])
app.include_router(cycles.router, prefix="/api/cycles", tags=["cycles"])
# app.include_router(labels.router, prefix="/api/labels", tags=["labels"])
app.include_router(cycle_updates.router, prefix="/api/cycles", tags=["cycle-updates"])
# app.include_router(git.router, prefix="/api/git", tags=["git"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Syncup API"}

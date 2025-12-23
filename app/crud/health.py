from sqlalchemy.orm import Session
from app.models.project import Project, Milestone
from app.schemas.health import InitiativeHealthSummary, ProjectHealthSummary, StatusDistribution
from typing import List, Dict
from app.core.constants import HealthStatus


def get_initiative_health_summary(
    db: Session,
    initiative_id: str
) -> InitiativeHealthSummary:
    # Get all projects under this initiative
    projects = db.query(Project).filter(Project.initiative_id == initiative_id).all()

    if not projects:
        return InitiativeHealthSummary(
            initiative_id=initiative_id,
            total_projects=0,
            status_distribution=StatusDistribution(
                on_track=0,
                at_risk=0,
                off_track=0,
                canceled=0,
                completed=0,
                backlog=0
            ),
            overall_health=HealthStatus.BACKLOG
        )
    # Initialize health counts
    health_counts = {
        HealthStatus.ON_TRACK: 0,
        HealthStatus.AT_RISK: 0,
        HealthStatus.OFF_TRACK: 0,
        HealthStatus.CANCELED: 0,
        HealthStatus.COMPLETED: 0,
        HealthStatus.BACKLOG: 0
    }
    
    # Count projects by status
    for project in projects:
        if project.status:
            try:
                status = HealthStatus(project.status)
                health_counts[status] += 1
            except ValueError:
                health_counts[HealthStatus.BACKLOG] += 1
        else:
            health_counts[HealthStatus.BACKLOG] += 1
    
    # Determine overall health based on project health distribution
    overall_health = determine_overall_health(health_counts)
    
    return InitiativeHealthSummary(
        initiative_id=initiative_id,
        total_projects=len(projects),
        status_distribution=StatusDistribution(
            on_track=health_counts[HealthStatus.ON_TRACK],
            at_risk=health_counts[HealthStatus.AT_RISK],
            off_track=health_counts[HealthStatus.OFF_TRACK],
            canceled=health_counts[HealthStatus.CANCELED],
            completed=health_counts[HealthStatus.COMPLETED],
            backlog=health_counts[HealthStatus.BACKLOG]
        ),
        overall_health=overall_health
    )

def get_project_health_summary(
    db: Session,
    project_id: str
) -> ProjectHealthSummary:
    # Get project details
    milestones = db.query(Milestone).filter(Milestone.project_id == project_id).all()

    if not milestones:
        return ProjectHealthSummary(
            project_id=project_id,
            total_projects=0,
            status_distribution=StatusDistribution(
                on_track=0,
                at_risk=0,
                off_track=0,
                canceled=0,
                completed=0,
                backlog=0
            ),
            overall_health=HealthStatus.BACKLOG
        )
    # Initialize health counts
    health_counts = {
        HealthStatus.ON_TRACK: 0,
        HealthStatus.AT_RISK: 0,
        HealthStatus.OFF_TRACK: 0,
        HealthStatus.CANCELED: 0,
        HealthStatus.COMPLETED: 0,
        HealthStatus.BACKLOG: 0
    }
    
    # Count projects by status
    for milestone in milestones:
        if milestone.status:
            try:
                status = HealthStatus(milestone.status)
                health_counts[status] += 1
            except ValueError:
                health_counts[HealthStatus.BACKLOG] += 1
        else:
            health_counts[HealthStatus.BACKLOG] += 1
    
    # Determine overall health based on project health distribution
    overall_health = determine_overall_health(health_counts)
    
    return ProjectHealthSummary(
        project_id=project_id,
        total_projects=len(milestones),
        status_distribution=StatusDistribution(
            on_track=health_counts[HealthStatus.ON_TRACK],
            at_risk=health_counts[HealthStatus.AT_RISK],
            off_track=health_counts[HealthStatus.OFF_TRACK],
            canceled=health_counts[HealthStatus.CANCELED],
            completed=health_counts[HealthStatus.COMPLETED],
            backlog=health_counts[HealthStatus.BACKLOG]
        ),
        overall_health=overall_health
    )

def determine_overall_health(health_counts: Dict[HealthStatus, int]) -> HealthStatus:
    # Logic to determine overall health
    if health_counts[HealthStatus.OFF_TRACK] > 0:
        return HealthStatus.OFF_TRACK
    elif health_counts[HealthStatus.AT_RISK] > 0:
        return HealthStatus.AT_RISK
    elif health_counts[HealthStatus.ON_TRACK] > 0:
        return HealthStatus.ON_TRACK
    elif health_counts[HealthStatus.CANCELED] > 0:
        return HealthStatus.CANCELED
    elif health_counts[HealthStatus.COMPLETED] > 0:
        return HealthStatus.COMPLETED
    else:
        return HealthStatus.BACKLOG 
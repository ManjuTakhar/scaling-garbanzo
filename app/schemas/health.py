from pydantic import BaseModel
from app.core.constants import HealthStatus

class HealthDistribution(BaseModel):
    on_track: int
    at_risk: int
    off_track: int
    canceled: int
    completed: int
    backlog: int

class ProjectsSummary(BaseModel):
    total_projects: int
    health_distribution: HealthDistribution

class StatusDistribution(BaseModel):
    on_track: int
    at_risk: int
    off_track: int
    canceled: int
    completed: int
    backlog: int

class InitiativeHealthSummary(BaseModel):
    initiative_id: str
    total_projects: int
    status_distribution: StatusDistribution
    overall_health: HealthStatus 

class ProjectHealthSummary(BaseModel):
    project_id: str
    total_projects: int
    status_distribution: StatusDistribution
    overall_health: HealthStatus 
from sqlalchemy import Table, Column, String, ForeignKey
from app.db.base import Base

project_teams = Table(
    "project_teams",
    Base.metadata,
    Column("project_id", String, ForeignKey("projects.project_id"), primary_key=True),
    Column("team_id", String, ForeignKey("teams.team_id"), primary_key=True)
) 
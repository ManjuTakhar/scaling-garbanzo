from sqlalchemy import Table, Column, String, ForeignKey
from app.db.base import Base

initiative_teams = Table(
    "initiative_teams",
    Base.metadata,
    Column("initiative_id", String, ForeignKey("initiatives.initiative_id"), primary_key=True),
    Column("team_id", String, ForeignKey("teams.team_id"), primary_key=True)
) 
from typing import List, Optional
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.cycle import Cycle as CycleModel, TeamCycleSequence
from app.models.issue import Issue as IssueModel
from app.models.teams import Team as TeamModel
from app.models.user import User as UserModel
from app.schemas.cycles import CycleCreate, CycleUpdate, CycleStatus, StartCycleRequest, CompleteCycleRequest
from app.dto.dtos import CycleDTO, TeamDTO, UserDTO, IssueDTO
from app.core.utils import generate_display_id


def _to_user_dto_min(db: Session, user_id: Optional[str]) -> Optional[UserDTO]:
    if not user_id:
        return None
    row = db.query(
        UserModel.user_id, UserModel.name, UserModel.email, UserModel.picture
    ).filter(UserModel.user_id == user_id).first()
    if not row:
        return None
    return UserDTO(user_id=row.user_id, name=row.name, email=row.email, picture=row.picture)


def _to_issue_dto_list(db: Session, issues: List[IssueModel]) -> Optional[List[IssueDTO]]:
    if not issues:
        return None
    result: List[IssueDTO] = []
    for issue in issues:
        assignee = _to_user_dto_min(db, issue.assignee)
        result.append(
            IssueDTO(
                id=issue.id,
                display_id=issue.display_id,
                title=issue.title,
                description=issue.description,
                status=issue.status,
                priority=issue.priority,
                issue_type=issue.issue_type,
                assignee=assignee,
                cycle_id=issue.cycle_id,
            )
        )
    return result


def _to_cycle_dto(db: Session, cycle: CycleModel, include_issues: bool = False) -> CycleDTO:
    created_by = _to_user_dto_min(db, cycle.created_by)
    updated_by = _to_user_dto_min(db, cycle.updated_by) if cycle.updated_by else None
    team = db.query(TeamModel).filter(TeamModel.team_id == cycle.team_id).first() if cycle.team_id else None

    return CycleDTO(
        id=cycle.id,
        display_id=cycle.display_id,
        name=cycle.name,
        status=cycle.status,
        start_date=int(cycle.start_date.timestamp()) if cycle.start_date else None,
        due_date=int(cycle.due_date.timestamp()) if cycle.due_date else None,
        completed_at=int(cycle.completed_at.timestamp()) if cycle.completed_at else None,
        created_at=int(cycle.created_at.timestamp()) if cycle.created_at else None,
        updated_at=int(cycle.updated_at.timestamp()) if cycle.updated_at else None,
        created_by=created_by,
        team_id=cycle.team_id,
        description=cycle.description,
        # Attach issues list only when requested to keep payload light
        # Not part of CycleDTO schema strictly, but safe to omit
    )


def _next_sequence(db: Session, team_id: str) -> int:
    entry = db.query(TeamCycleSequence).filter(TeamCycleSequence.team_id == team_id).first()
    if not entry:
        entry = TeamCycleSequence(team_id=team_id, sequence_number=0)
        db.add(entry)
    entry.sequence_number += 1
    db.commit()
    return entry.sequence_number


def create_cycle(db: Session, cycle_data: dict) -> CycleDTO:
    payload = CycleCreate(**cycle_data)

    db_cycle = CycleModel(
        name=payload.name,
        start_date=datetime.fromtimestamp(payload.start_date) if payload.start_date else None,
        due_date=datetime.fromtimestamp(payload.due_date) if payload.due_date else None,
        created_by=payload.created_by,
        updated_by=payload.created_by,
        team_id=payload.team_id,
        description=payload.description,
        status=CycleStatus.ACTIVE,
    )

    team = None
    if payload.team_id:
        team = db.query(TeamModel).filter(TeamModel.team_id == payload.team_id).first()
        if team:
            seq = _next_sequence(db, payload.team_id)
            db_cycle.display_id = generate_display_id(team.name, seq)

    db.add(db_cycle)
    db.commit()
    db.refresh(db_cycle)
    return _to_cycle_dto(db, db_cycle)


def get_cycle(db: Session, cycle_id: str) -> Optional[CycleDTO]:
    cycle = db.query(CycleModel).filter(CycleModel.id == cycle_id).first()
    if not cycle:
        return None
    return _to_cycle_dto(db, cycle)


def get_cycles(db: Session, team_id: Optional[str] = None, status: Optional[str] = None) -> List[CycleDTO]:
    query = db.query(CycleModel)
    if team_id:
        query = query.filter(CycleModel.team_id == team_id)
    if status:
        query = query.filter(CycleModel.status == status)
    rows = query.order_by(CycleModel.created_at.desc()).all()
    return [_to_cycle_dto(db, c) for c in rows]


def update_cycle(db: Session, cycle_id: str, cycle_data: dict) -> CycleDTO:
    db_cycle = db.query(CycleModel).filter(CycleModel.id == cycle_id).first()
    if not db_cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")

    update = CycleUpdate(**cycle_data)
    if update.name is not None:
        db_cycle.name = update.name
    if update.description is not None:
        db_cycle.description = update.description
    if update.start_date is not None:
        db_cycle.start_date = datetime.fromtimestamp(update.start_date)
    if update.due_date is not None:
        db_cycle.due_date = datetime.fromtimestamp(update.due_date)
    if update.status is not None:
        db_cycle.status = update.status
    if update.updated_by is not None:
        db_cycle.updated_by = update.updated_by

    db.commit()
    db.refresh(db_cycle)
    return _to_cycle_dto(db, db_cycle)


def delete_cycle(db: Session, cycle_id: str) -> None:
    db_cycle = db.query(CycleModel).filter(CycleModel.id == cycle_id).first()
    if not db_cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    db.delete(db_cycle)
    db.commit()


def start_cycle(db: Session, cycle_id: str, payload: StartCycleRequest) -> CycleDTO:
    db_cycle = db.query(CycleModel).filter(CycleModel.id == cycle_id).first()
    if not db_cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    db_cycle.status = CycleStatus.ACTIVE
    db_cycle.updated_by = payload.started_by
    db_cycle.started_by = payload.started_by
    db_cycle.started_at = datetime.utcnow()
    db.commit()
    db.refresh(db_cycle)
    return _to_cycle_dto(db, db_cycle)


def complete_cycle(db: Session, cycle_id: str, payload: CompleteCycleRequest) -> CycleDTO:
    db_cycle = db.query(CycleModel).filter(CycleModel.id == cycle_id).first()
    if not db_cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    db_cycle.status = CycleStatus.COMPLETED
    db_cycle.completed_at = datetime.utcnow()
    db_cycle.completed_by = payload.completed_by
    db_cycle.updated_by = payload.completed_by

    # Move explicitly listed issues
    if payload.issues_to_move:
        for issue_id in payload.issues_to_move:
            issue = db.query(IssueModel).filter(IssueModel.id == issue_id).first()
            if not issue or issue.cycle_id != cycle_id:
                continue
            if payload.move_to_backlog:
                issue.cycle_id = None
                issue.status = "BACKLOG"
                issue.updated_by = payload.completed_by
            elif payload.new_cycle_id:
                issue.cycle_id = payload.new_cycle_id
                issue.updated_by = payload.completed_by

    db.commit()
    db.refresh(db_cycle)
    return _to_cycle_dto(db, db_cycle)


def get_complete_cycle_info(db: Session, cycle_id: str):
    db_cycle = db.query(CycleModel).filter(CycleModel.id == cycle_id).first()
    if not db_cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    issues = db.query(IssueModel).filter(IssueModel.cycle_id == cycle_id).all()
    return {
        "cycle": _to_cycle_dto(db, db_cycle),
        "issues": _to_issue_dto_list(db, issues),
    }



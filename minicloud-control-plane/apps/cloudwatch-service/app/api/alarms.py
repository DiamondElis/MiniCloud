from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import Caller, audit_success, require_cloudwatch_auth
from app.core.errors import conflict, not_found
from app.db.session import get_db
from app.engine.alarm_evaluator import evaluate_alarm
from app.models.alarm import AlarmDefinition, AlarmStateHistory
from app.schemas.requests import CreateAlarmRequest
from app.schemas.responses import AlarmEvaluationResponse, AlarmHistoryResponse, AlarmResponse

router = APIRouter(prefix="/cloudwatch/alarms", tags=["alarms"])


@router.post("", response_model=AlarmResponse)
def create_alarm(
    payload: CreateAlarmRequest,
    request: Request,
    _: Caller = Depends(require_cloudwatch_auth("cloudwatch:PutMetricAlarm", "alarm/*")),
    db: Session = Depends(get_db),
) -> AlarmDefinition:
    alarm = AlarmDefinition(**payload.model_dump(), state="INSUFFICIENT_DATA")
    db.add(alarm)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise conflict("Duplicate alarm") from exc
    db.refresh(alarm)
    audit_success(request, db, {"alarm": alarm.name})
    return alarm


@router.get("", response_model=list[AlarmResponse])
def list_alarms(
    request: Request,
    _: Caller = Depends(require_cloudwatch_auth("cloudwatch:DescribeAlarms", "alarm/*")),
    db: Session = Depends(get_db),
) -> list[AlarmDefinition]:
    alarms = list(db.execute(select(AlarmDefinition).order_by(AlarmDefinition.name)).scalars())
    audit_success(request, db)
    return alarms


@router.get("/{alarm_name}", response_model=AlarmResponse)
def get_alarm(
    alarm_name: str,
    request: Request,
    _: Caller = Depends(require_cloudwatch_auth("cloudwatch:DescribeAlarms", "alarm/*")),
    db: Session = Depends(get_db),
) -> AlarmDefinition:
    alarm = db.execute(select(AlarmDefinition).where(AlarmDefinition.name == alarm_name)).scalar_one_or_none()
    if not alarm:
        raise not_found("Alarm not found")
    audit_success(request, db, {"alarm": alarm.name})
    return alarm


@router.post("/{alarm_name}/evaluate", response_model=AlarmEvaluationResponse)
def evaluate_alarm_endpoint(
    alarm_name: str,
    request: Request,
    _: Caller = Depends(require_cloudwatch_auth("cloudwatch:DescribeAlarms", "alarm/*")),
    db: Session = Depends(get_db),
) -> AlarmEvaluationResponse:
    alarm = db.execute(select(AlarmDefinition).where(AlarmDefinition.name == alarm_name)).scalar_one_or_none()
    if not alarm:
        raise not_found("Alarm not found")
    result = evaluate_alarm(db, alarm)
    audit_success(request, db, {"alarm": alarm.name, "new_state": result.new_state})
    return AlarmEvaluationResponse(**result.__dict__)


@router.get("/{alarm_name}/history", response_model=list[AlarmHistoryResponse])
def alarm_history(
    alarm_name: str,
    request: Request,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    _: Caller = Depends(require_cloudwatch_auth("cloudwatch:DescribeAlarms", "alarm/*")),
    db: Session = Depends(get_db),
) -> list[AlarmStateHistory]:
    alarm = db.execute(select(AlarmDefinition).where(AlarmDefinition.name == alarm_name)).scalar_one_or_none()
    if not alarm:
        raise not_found("Alarm not found")
    rows = list(
        db.execute(
            select(AlarmStateHistory)
            .where(AlarmStateHistory.alarm_id == alarm.id)
            .order_by(AlarmStateHistory.created_at.desc())
            .limit(limit)
            .offset(offset)
        ).scalars()
    )
    audit_success(request, db, {"alarm": alarm.name})
    return rows


@router.delete("/{alarm_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alarm(
    alarm_name: str,
    request: Request,
    _: Caller = Depends(require_cloudwatch_auth("cloudwatch:DeleteAlarms", "alarm/*")),
    db: Session = Depends(get_db),
) -> None:
    alarm = db.execute(select(AlarmDefinition).where(AlarmDefinition.name == alarm_name)).scalar_one_or_none()
    if not alarm:
        raise not_found("Alarm not found")
    db.delete(alarm)
    db.commit()
    audit_success(request, db, {"alarm": alarm_name})


from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.auth import Caller, audit_success, require_cloudwatch_auth
from app.core.errors import not_found
from app.core.time import ensure_utc
from app.db.session import get_db
from app.engine.log_normalizer import normalize_log_event
from app.models.log_event import LogEvent
from app.repositories.logs_repo import get_log_group, get_log_stream, query_logs
from app.schemas.requests import PutLogRequest
from app.schemas.responses import LogEventResponse

router = APIRouter(prefix="/cloudwatch", tags=["logs"])


@router.post("/logs", response_model=LogEventResponse)
def put_log(
    payload: PutLogRequest,
    request: Request,
    _: Caller = Depends(require_cloudwatch_auth("cloudwatch:PutLogEvents", "log-stream/*")),
    db: Session = Depends(get_db),
) -> LogEvent:
    group = get_log_group(db, payload.log_group)
    if not group:
        raise not_found("Log group not found")
    stream = get_log_stream(db, group.id, payload.log_stream)
    if not stream:
        raise not_found("Log stream not found")
    normalized = normalize_log_event(payload.event, payload.message)
    log = LogEvent(
        log_group_id=group.id,
        log_stream_id=stream.id,
        timestamp=ensure_utc(payload.timestamp),
        message=normalized["message"],
        event=payload.event,
        request_id=normalized["request_id"],
        principal=normalized["principal"],
        service=normalized["service"],
        action=normalized["action"],
        resource=normalized["resource"],
        status=normalized["status"],
        level=normalized["level"] or "INFO",
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    audit_success(request, db, {"log_group": payload.log_group, "log_stream": payload.log_stream})
    return log


@router.get("/logs", response_model=list[LogEventResponse])
def get_logs(
    request: Request,
    log_group: str | None = None,
    log_stream: str | None = None,
    service: str | None = None,
    action: str | None = None,
    status: str | None = None,
    principal: str | None = None,
    request_id: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    _: Caller = Depends(require_cloudwatch_auth("cloudwatch:GetLogEvents", "log-group/*")),
    db: Session = Depends(get_db),
) -> list[LogEvent]:
    logs = query_logs(
        db,
        log_group=log_group,
        log_stream=log_stream,
        service=service,
        action=action,
        status=status,
        principal=principal,
        request_id=request_id,
        start_time=ensure_utc(start_time) if start_time else None,
        end_time=ensure_utc(end_time) if end_time else None,
        limit=limit,
        offset=offset,
    )
    audit_success(request, db)
    return logs


@router.get("/log-groups/{group_name:path}/streams/{stream_name:path}/events", response_model=list[LogEventResponse])
def get_stream_events(
    group_name: str,
    stream_name: str,
    request: Request,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    _: Caller = Depends(require_cloudwatch_auth("cloudwatch:GetLogEvents", "log-stream/*")),
    db: Session = Depends(get_db),
) -> list[LogEvent]:
    if not get_log_group(db, group_name):
        raise not_found("Log group not found")
    logs = query_logs(db, log_group=group_name, log_stream=stream_name, limit=limit, offset=offset, ascending=True)
    audit_success(request, db, {"log_group": group_name, "log_stream": stream_name})
    return logs


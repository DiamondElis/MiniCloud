from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import Caller, audit_success, require_cloudwatch_auth
from app.core.errors import conflict, not_found
from app.db.session import get_db
from app.models.log_group import LogGroup
from app.models.log_stream import LogStream
from app.schemas.requests import CreateLogStreamRequest
from app.schemas.responses import LogStreamResponse

router = APIRouter(tags=["log-streams"])


@router.post("/cloudwatch/log-streams", response_model=LogStreamResponse)
def create_log_stream(
    payload: CreateLogStreamRequest,
    request: Request,
    _: Caller = Depends(require_cloudwatch_auth("cloudwatch:CreateLogStream", "log-stream/*")),
    db: Session = Depends(get_db),
) -> LogStream:
    group = db.execute(select(LogGroup).where(LogGroup.name == payload.log_group)).scalar_one_or_none()
    if not group:
        raise not_found("Log group not found")
    stream = LogStream(log_group_id=group.id, name=payload.name, source_service=payload.source_service, resource_id=payload.resource_id)
    db.add(stream)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise conflict("Duplicate log stream") from exc
    db.refresh(stream)
    audit_success(request, db, {"log_group": payload.log_group, "log_stream": payload.name})
    return stream


@router.get("/cloudwatch/log-groups/{group_name:path}/streams", response_model=list[LogStreamResponse])
def list_log_streams(
    group_name: str,
    request: Request,
    _: Caller = Depends(require_cloudwatch_auth("cloudwatch:GetLogEvents", "log-stream/*")),
    db: Session = Depends(get_db),
) -> list[LogStream]:
    group = db.execute(select(LogGroup).where(LogGroup.name == group_name)).scalar_one_or_none()
    if not group:
        raise not_found("Log group not found")
    streams = list(db.execute(select(LogStream).where(LogStream.log_group_id == group.id).order_by(LogStream.name)).scalars())
    audit_success(request, db, {"log_group": group_name})
    return streams


from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.log_event import LogEvent
from app.models.log_group import LogGroup
from app.models.log_stream import LogStream


def get_log_group(db: Session, name: str) -> LogGroup | None:
    return db.execute(select(LogGroup).where(LogGroup.name == name)).scalar_one_or_none()


def get_log_stream(db: Session, group_id: str, name: str) -> LogStream | None:
    return db.execute(
        select(LogStream).where(LogStream.log_group_id == group_id, LogStream.name == name)
    ).scalar_one_or_none()


def query_logs(
    db: Session,
    *,
    log_group: str | None = None,
    log_stream: str | None = None,
    service: str | None = None,
    action: str | None = None,
    status: str | None = None,
    principal: str | None = None,
    request_id: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
    ascending: bool = False,
) -> list[LogEvent]:
    stmt = select(LogEvent).join(LogGroup, LogEvent.log_group_id == LogGroup.id).join(
        LogStream, LogEvent.log_stream_id == LogStream.id
    )
    if log_group:
        stmt = stmt.where(LogGroup.name == log_group)
    if log_stream:
        stmt = stmt.where(LogStream.name == log_stream)
    for column, value in [
        (LogEvent.service, service),
        (LogEvent.action, action),
        (LogEvent.status, status),
        (LogEvent.principal, principal),
        (LogEvent.request_id, request_id),
    ]:
        if value:
            stmt = stmt.where(column == value)
    if start_time:
        stmt = stmt.where(LogEvent.timestamp >= start_time)
    if end_time:
        stmt = stmt.where(LogEvent.timestamp <= end_time)
    stmt = stmt.order_by(LogEvent.timestamp.asc() if ascending else LogEvent.timestamp.desc())
    return list(db.execute(stmt.limit(limit).offset(offset)).scalars())


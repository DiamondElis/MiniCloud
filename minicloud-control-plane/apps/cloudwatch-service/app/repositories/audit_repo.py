from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.time import utcnow
from app.models.audit_event import AuditEvent


def write_audit(
    db: Session,
    *,
    principal: str | None,
    action: str,
    resource: str | None,
    status: str = "Success",
    decision: str | None = None,
    detail: dict | None = None,
) -> AuditEvent:
    event = AuditEvent(
        principal=principal,
        service="cloudwatch",
        action=action,
        resource=resource,
        decision=decision,
        status=status,
        timestamp=utcnow(),
        detail=detail or {},
    )
    db.add(event)
    db.commit()
    return event


def query_audit_events(db: Session, limit: int = 100, offset: int = 0, **filters: str | datetime | None) -> list[AuditEvent]:
    stmt = select(AuditEvent)
    for key in ["service", "action", "resource", "principal", "decision", "status", "request_id"]:
        value = filters.get(key)
        if value:
            stmt = stmt.where(getattr(AuditEvent, key) == value)
    if filters.get("start_time"):
        stmt = stmt.where(AuditEvent.timestamp >= filters["start_time"])
    if filters.get("end_time"):
        stmt = stmt.where(AuditEvent.timestamp <= filters["end_time"])
    return list(db.execute(stmt.order_by(AuditEvent.timestamp.desc()).limit(limit).offset(offset)).scalars())

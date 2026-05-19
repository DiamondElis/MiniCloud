from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.auth import Caller, require_cloudwatch_auth
from app.core.time import ensure_utc
from app.db.session import get_db
from app.models.audit_event import AuditEvent
from app.repositories.audit_repo import query_audit_events
from app.schemas.requests import PutAuditEventRequest
from app.schemas.responses import AuditEventResponse

router = APIRouter(prefix="/cloudwatch/audit-events", tags=["audit-events"])


@router.post("", response_model=AuditEventResponse)
def put_audit_event(
    payload: PutAuditEventRequest,
    _: Caller = Depends(require_cloudwatch_auth("cloudwatch:PutAuditEvent", "audit-event/*", skip_audit=True)),
    db: Session = Depends(get_db),
) -> AuditEvent:
    event = AuditEvent(
        request_id=payload.request_id,
        principal=payload.principal,
        service=payload.service,
        action=payload.action,
        resource=payload.resource,
        decision=payload.decision,
        status=payload.status,
        error_code=payload.error_code,
        source_ip=payload.source_ip,
        user_agent=payload.user_agent,
        timestamp=ensure_utc(payload.timestamp),
        detail=payload.detail,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("", response_model=list[AuditEventResponse])
def get_audit_events(
    request: Request,
    service: str | None = None,
    action: str | None = None,
    resource: str | None = None,
    principal: str | None = None,
    decision: str | None = None,
    status: str | None = None,
    request_id: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    _: Caller = Depends(require_cloudwatch_auth("cloudwatch:GetAuditEvents", "audit-event/*", skip_audit=True)),
    db: Session = Depends(get_db),
) -> list[AuditEvent]:
    return query_audit_events(
        db,
        limit=limit,
        offset=offset,
        service=service,
        action=action,
        resource=resource,
        principal=principal,
        decision=decision,
        status=status,
        request_id=request_id,
        start_time=ensure_utc(start_time) if start_time else None,
        end_time=ensure_utc(end_time) if end_time else None,
    )


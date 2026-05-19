from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent


def write_audit_event(db: Session, event: AuditEvent) -> AuditEvent:
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


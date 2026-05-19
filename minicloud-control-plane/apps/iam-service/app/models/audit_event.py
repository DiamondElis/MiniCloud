from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, new_uuid


class AuditEvent(TimestampMixin, Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    request_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    principal_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    principal_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    action: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resource: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    decision: Mapped[str | None] = mapped_column(String(32), nullable=True)
    reason: Mapped[str | None] = mapped_column(String(64), nullable=True)
    matched_policy_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    source_ip: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    service: Mapped[str | None] = mapped_column(String(255), nullable=True)


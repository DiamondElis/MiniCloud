from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.resource_ids import new_uuid
from app.core.time import utcnow
from app.db.base import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    request_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    principal: Mapped[str | None] = mapped_column(String(512), nullable=True, index=True)
    service: Mapped[str] = mapped_column(String(128), index=True)
    action: Mapped[str] = mapped_column(String(255), index=True)
    resource: Mapped[str | None] = mapped_column(String(1024), nullable=True, index=True)
    decision: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    status: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    error_code: Mapped[str | None] = mapped_column(String(128), nullable=True)
    source_ip: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    detail: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    ingestion_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


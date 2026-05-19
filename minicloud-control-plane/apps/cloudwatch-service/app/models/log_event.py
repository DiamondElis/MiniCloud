from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.resource_ids import new_uuid
from app.core.time import utcnow
from app.db.base import Base


class LogEvent(Base):
    __tablename__ = "log_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    log_group_id: Mapped[str] = mapped_column(ForeignKey("log_groups.id", ondelete="CASCADE"), index=True)
    log_stream_id: Mapped[str] = mapped_column(ForeignKey("log_streams.id", ondelete="CASCADE"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    ingestion_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    event: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    principal: Mapped[str | None] = mapped_column(String(512), nullable=True, index=True)
    service: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    action: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    resource: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    status: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    level: Mapped[str] = mapped_column(String(32), default="INFO")


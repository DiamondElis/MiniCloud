from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.resource_ids import new_uuid
from app.core.time import utcnow
from app.db.base import Base


class EventBus(Base):
    __tablename__ = "event_buses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    event_bus_id: Mapped[str] = mapped_column(ForeignKey("event_buses.id", ondelete="CASCADE"), index=True)
    source: Mapped[str] = mapped_column(String(255), index=True)
    detail_type: Mapped[str] = mapped_column(String(255), index=True)
    detail: Mapped[dict[str, Any]] = mapped_column(JSON)
    resources: Mapped[list[str]] = mapped_column(JSON, default=list)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    request_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


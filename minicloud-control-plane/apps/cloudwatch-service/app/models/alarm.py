from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.resource_ids import new_uuid
from app.core.time import utcnow
from app.db.base import Base


class AlarmDefinition(Base):
    __tablename__ = "alarm_definitions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    namespace: Mapped[str] = mapped_column(String(255), index=True)
    metric_name: Mapped[str] = mapped_column(String(255), index=True)
    dimensions: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    statistic: Mapped[str] = mapped_column(String(32), default="Sum")
    period_seconds: Mapped[int] = mapped_column(Integer, default=60)
    evaluation_periods: Mapped[int] = mapped_column(Integer, default=1)
    datapoints_to_alarm: Mapped[int] = mapped_column(Integer, default=1)
    comparison_operator: Mapped[str] = mapped_column(String(64))
    threshold: Mapped[float] = mapped_column(Float)
    state: Mapped[str] = mapped_column(String(32), default="INSUFFICIENT_DATA")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class AlarmStateHistory(Base):
    __tablename__ = "alarm_state_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    alarm_id: Mapped[str] = mapped_column(ForeignKey("alarm_definitions.id", ondelete="CASCADE"), index=True)
    old_state: Mapped[str | None] = mapped_column(String(32), nullable=True)
    new_state: Mapped[str] = mapped_column(String(32))
    reason: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    evaluated_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


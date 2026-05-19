from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.resource_ids import new_uuid
from app.core.time import utcnow
from app.db.base import Base


class MetricDatapoint(Base):
    __tablename__ = "metric_datapoints"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    namespace: Mapped[str] = mapped_column(String(255), index=True)
    metric_name: Mapped[str] = mapped_column(String(255), index=True)
    dimensions: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    resource_id: Mapped[str | None] = mapped_column(String(512), nullable=True, index=True)
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(32))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    ingestion_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


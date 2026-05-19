from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.resource_ids import new_uuid
from app.core.time import utcnow
from app.db.base import Base


class LogGroup(Base):
    __tablename__ = "log_groups"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(512), unique=True, index=True)
    retention_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    kms_key_id: Mapped[str | None] = mapped_column(String(512), nullable=True)
    tags: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    streams: Mapped[list["LogStream"]] = relationship(back_populates="group", cascade="all, delete-orphan")


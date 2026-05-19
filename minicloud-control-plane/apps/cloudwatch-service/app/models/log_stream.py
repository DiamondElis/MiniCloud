from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.resource_ids import new_uuid
from app.core.time import utcnow
from app.db.base import Base


class LogStream(Base):
    __tablename__ = "log_streams"
    __table_args__ = (UniqueConstraint("log_group_id", "name", name="uq_log_stream_group_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    log_group_id: Mapped[str] = mapped_column(ForeignKey("log_groups.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(512), index=True)
    source_service: Mapped[str | None] = mapped_column(String(128), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    group: Mapped["LogGroup"] = relationship(back_populates="streams")


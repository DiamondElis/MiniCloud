from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, new_uuid


class AccessKey(TimestampMixin, Base):
    __tablename__ = "access_keys"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    access_key_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    secret_key_hash: Mapped[str] = mapped_column(String(255))
    principal_type: Mapped[str] = mapped_column(String(64), index=True)
    principal_id: Mapped[str] = mapped_column(String(36), index=True)
    status: Mapped[str] = mapped_column(String(32), default="active")
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


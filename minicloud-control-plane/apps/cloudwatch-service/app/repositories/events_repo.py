from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.event import EventBus


DEFAULT_BUSES = ("default", "security", "platform")


def seed_default_buses(db: Session) -> None:
    for name in DEFAULT_BUSES:
        if not db.execute(select(EventBus).where(EventBus.name == name)).scalar_one_or_none():
            db.add(EventBus(name=name))
    db.commit()


def get_event_bus(db: Session, name: str) -> EventBus | None:
    return db.execute(select(EventBus).where(EventBus.name == name)).scalar_one_or_none()


from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import Group, User


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.execute(select(User).where(User.username == username)).scalar_one_or_none()


def get_group_by_name(db: Session, name: str) -> Group | None:
    return db.execute(select(Group).where(Group.name == name)).scalar_one_or_none()


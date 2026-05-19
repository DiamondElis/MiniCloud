from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.access_key import AccessKey
from app.models.session import SessionToken


def get_access_key(db: Session, access_key_id: str) -> AccessKey | None:
    return db.execute(select(AccessKey).where(AccessKey.access_key_id == access_key_id)).scalar_one_or_none()


def get_session(db: Session, session_id: str) -> SessionToken | None:
    return db.get(SessionToken, session_id)


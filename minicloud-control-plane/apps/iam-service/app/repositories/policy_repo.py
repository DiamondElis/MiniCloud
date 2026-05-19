from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.policy import Policy


def list_policies(db: Session) -> list[Policy]:
    return list(db.execute(select(Policy).order_by(Policy.name)).scalars())


def get_policy(db: Session, policy_id: str) -> Policy | None:
    return db.get(Policy, policy_id)


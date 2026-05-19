from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.alarm import AlarmDefinition


def matching_alarms(db: Session, namespace: str, metric_name: str, dimensions: dict) -> list[AlarmDefinition]:
    rows = db.execute(
        select(AlarmDefinition).where(
            AlarmDefinition.namespace == namespace,
            AlarmDefinition.metric_name == metric_name,
            AlarmDefinition.enabled.is_(True),
        )
    ).scalars()
    return [alarm for alarm in rows if alarm.dimensions == dimensions]


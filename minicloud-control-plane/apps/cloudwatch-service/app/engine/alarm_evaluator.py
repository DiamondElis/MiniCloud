from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.time import utcnow
from app.engine.metric_aggregator import aggregate, compare
from app.models.alarm import AlarmDefinition, AlarmStateHistory
from app.models.event import Event
from app.models.metric import MetricDatapoint
from app.repositories.events_repo import get_event_bus


@dataclass(frozen=True)
class AlarmEvaluation:
    alarm_name: str
    old_state: str | None
    new_state: str
    reason: str
    evaluated_value: float | None


def _values_for_alarm(db: Session, alarm: AlarmDefinition) -> list[float]:
    end = utcnow()
    start = end - timedelta(seconds=alarm.period_seconds * alarm.evaluation_periods)
    rows = db.execute(
        select(MetricDatapoint).where(
            MetricDatapoint.namespace == alarm.namespace,
            MetricDatapoint.metric_name == alarm.metric_name,
            MetricDatapoint.timestamp >= start,
            MetricDatapoint.timestamp <= end,
        )
    ).scalars()
    return [row.value for row in rows if row.dimensions == alarm.dimensions]


def evaluate_alarm(db: Session, alarm: AlarmDefinition) -> AlarmEvaluation:
    old_state = alarm.state
    values = _values_for_alarm(db, alarm)
    evaluated = aggregate(values, alarm.statistic)
    if evaluated is None:
        new_state = "INSUFFICIENT_DATA"
        reason = f"No datapoints for {alarm.metric_name}"
    elif compare(evaluated, alarm.comparison_operator, alarm.threshold):
        new_state = "ALARM"
        reason = f"{alarm.statistic} of {alarm.metric_name} was {evaluated:g}, threshold is {alarm.threshold:g}"
    else:
        new_state = "OK"
        reason = f"{alarm.statistic} of {alarm.metric_name} was {evaluated:g}, threshold is {alarm.threshold:g}"

    if old_state != new_state:
        alarm.state = new_state
        db.add(
            AlarmStateHistory(
                alarm_id=alarm.id,
                old_state=old_state,
                new_state=new_state,
                reason=reason,
                evaluated_value=evaluated,
            )
        )
        platform_bus = get_event_bus(db, "platform")
        if platform_bus:
            db.add(
                Event(
                    event_bus_id=platform_bus.id,
                    source="minicloud.cloudwatch",
                    detail_type="CloudWatch Alarm State Change",
                    resources=[f"alarm/{alarm.name}"],
                    detail={
                        "alarm_name": alarm.name,
                        "old_state": old_state,
                        "new_state": new_state,
                        "reason": reason,
                        "evaluated_value": evaluated,
                    },
                    timestamp=utcnow(),
                )
            )
    db.commit()
    return AlarmEvaluation(alarm.name, old_state, new_state, reason, evaluated)


from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.metric import MetricDatapoint


def dimensions_match(candidate: dict[str, Any], expected: dict[str, Any] | None) -> bool:
    return not expected or candidate == expected


def query_metrics(
    db: Session,
    *,
    namespace: str | None = None,
    metric_name: str | None = None,
    resource_id: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    dimensions: dict[str, Any] | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[MetricDatapoint]:
    stmt = select(MetricDatapoint)
    if namespace:
        stmt = stmt.where(MetricDatapoint.namespace == namespace)
    if metric_name:
        stmt = stmt.where(MetricDatapoint.metric_name == metric_name)
    if resource_id:
        stmt = stmt.where(MetricDatapoint.resource_id == resource_id)
    if start_time:
        stmt = stmt.where(MetricDatapoint.timestamp >= start_time)
    if end_time:
        stmt = stmt.where(MetricDatapoint.timestamp <= end_time)
    stmt = stmt.order_by(MetricDatapoint.timestamp.desc())
    rows = list(db.execute(stmt).scalars())
    rows = [row for row in rows if dimensions_match(row.dimensions, dimensions)]
    return rows[offset : offset + limit]


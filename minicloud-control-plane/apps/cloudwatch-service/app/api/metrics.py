from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.auth import Caller, audit_success, require_cloudwatch_auth
from app.core.errors import bad_request
from app.core.time import ensure_utc
from app.db.session import get_db
from app.engine.alarm_evaluator import evaluate_alarm
from app.engine.metric_aggregator import aggregate
from app.models.metric import MetricDatapoint
from app.repositories.alarms_repo import matching_alarms
from app.repositories.metrics_repo import query_metrics
from app.schemas.requests import PutMetricRequest, SUPPORTED_STATISTICS
from app.schemas.responses import MetricResponse, MetricStatisticsResponse

router = APIRouter(prefix="/cloudwatch/metrics", tags=["metrics"])


@router.post("", response_model=MetricResponse)
def put_metric(
    payload: PutMetricRequest,
    request: Request,
    _: Caller = Depends(require_cloudwatch_auth("cloudwatch:PutMetricData", "metric/*")),
    db: Session = Depends(get_db),
) -> MetricDatapoint:
    metric = MetricDatapoint(
        namespace=payload.namespace,
        metric_name=payload.metric_name,
        dimensions=payload.dimensions,
        resource_id=payload.resource_id,
        value=payload.value,
        unit=payload.unit,
        timestamp=ensure_utc(payload.timestamp),
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    for alarm in matching_alarms(db, payload.namespace, payload.metric_name, payload.dimensions):
        evaluate_alarm(db, alarm)
    audit_success(request, db, {"namespace": payload.namespace, "metric_name": payload.metric_name})
    return metric


@router.get("", response_model=list[MetricResponse])
def get_metrics(
    request: Request,
    namespace: str | None = None,
    metric_name: str | None = None,
    resource_id: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    _: Caller = Depends(require_cloudwatch_auth("cloudwatch:GetMetricData", "metric/*")),
    db: Session = Depends(get_db),
) -> list[MetricDatapoint]:
    metrics = query_metrics(
        db,
        namespace=namespace,
        metric_name=metric_name,
        resource_id=resource_id,
        start_time=ensure_utc(start_time) if start_time else None,
        end_time=ensure_utc(end_time) if end_time else None,
        limit=limit,
        offset=offset,
    )
    audit_success(request, db)
    return metrics


@router.get("/statistics", response_model=MetricStatisticsResponse)
def metric_statistics(
    request: Request,
    namespace: str,
    metric_name: str,
    period: int = Query(60, ge=1),
    statistic: str = "Average",
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    _: Caller = Depends(require_cloudwatch_auth("cloudwatch:GetMetricStatistics", "metric/*")),
    db: Session = Depends(get_db),
) -> MetricStatisticsResponse:
    if statistic not in SUPPORTED_STATISTICS:
        raise bad_request("Unsupported statistic")
    metrics = query_metrics(
        db,
        namespace=namespace,
        metric_name=metric_name,
        start_time=ensure_utc(start_time) if start_time else None,
        end_time=ensure_utc(end_time) if end_time else None,
        limit=1000,
    )
    value = aggregate([metric.value for metric in metrics], statistic)
    audit_success(request, db, {"namespace": namespace, "metric_name": metric_name, "period": period})
    return MetricStatisticsResponse(namespace=namespace, metric_name=metric_name, statistic=statistic, value=value, datapoints=len(metrics))


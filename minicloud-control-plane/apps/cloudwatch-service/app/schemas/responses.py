from datetime import datetime
from typing import Any

from pydantic import BaseModel


class LogGroupResponse(BaseModel):
    id: str
    name: str
    retention_days: int | None
    kms_key_id: str | None
    tags: dict[str, Any]
    created_at: datetime
    model_config = {"from_attributes": True}


class LogStreamResponse(BaseModel):
    id: str
    log_group_id: str
    name: str
    source_service: str | None
    resource_id: str | None
    created_at: datetime
    model_config = {"from_attributes": True}


class LogEventResponse(BaseModel):
    id: str
    log_group_id: str
    log_stream_id: str
    timestamp: datetime
    ingestion_time: datetime
    message: str | None
    event: dict[str, Any] | None
    request_id: str | None
    principal: str | None
    service: str | None
    action: str | None
    resource: str | None
    status: str | None
    level: str
    model_config = {"from_attributes": True}


class MetricResponse(BaseModel):
    id: str
    namespace: str
    metric_name: str
    dimensions: dict[str, Any]
    resource_id: str | None
    value: float
    unit: str
    timestamp: datetime
    ingestion_time: datetime
    model_config = {"from_attributes": True}


class MetricStatisticsResponse(BaseModel):
    namespace: str
    metric_name: str
    statistic: str
    value: float | None
    datapoints: int


class EventBusResponse(BaseModel):
    id: str
    name: str
    created_at: datetime
    model_config = {"from_attributes": True}


class EventResponse(BaseModel):
    id: str
    event_bus_id: str
    source: str
    detail_type: str
    detail: dict[str, Any]
    resources: list[str]
    timestamp: datetime
    request_id: str | None
    created_at: datetime
    model_config = {"from_attributes": True}


class AlarmResponse(BaseModel):
    id: str
    name: str
    namespace: str
    metric_name: str
    dimensions: dict[str, Any]
    statistic: str
    period_seconds: int
    evaluation_periods: int
    datapoints_to_alarm: int
    comparison_operator: str
    threshold: float
    state: str
    enabled: bool
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class AlarmEvaluationResponse(BaseModel):
    alarm_name: str
    old_state: str | None
    new_state: str
    reason: str
    evaluated_value: float | None


class AlarmHistoryResponse(BaseModel):
    id: str
    alarm_id: str
    old_state: str | None
    new_state: str
    reason: str | None
    evaluated_value: float | None
    created_at: datetime
    model_config = {"from_attributes": True}


class AuditEventResponse(BaseModel):
    id: str
    request_id: str | None
    principal: str | None
    service: str
    action: str
    resource: str | None
    decision: str | None
    status: str | None
    error_code: str | None
    source_ip: str | None
    user_agent: str | None
    timestamp: datetime
    detail: dict[str, Any]
    ingestion_time: datetime
    model_config = {"from_attributes": True}


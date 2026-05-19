from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


SUPPORTED_UNITS = {"Count", "Percent", "Seconds", "Milliseconds", "Bytes", "Kilobytes", "Megabytes", "None"}
SUPPORTED_STATISTICS = {"Sum", "Average", "Minimum", "Maximum", "Count"}
SUPPORTED_COMPARISONS = {
    "GreaterThanThreshold",
    "GreaterThanOrEqualToThreshold",
    "LessThanThreshold",
    "LessThanOrEqualToThreshold",
    "EqualToThreshold",
}


class CreateLogGroupRequest(BaseModel):
    name: str
    retention_days: int | None = Field(default=None, ge=1)
    kms_key_id: str | None = None
    tags: dict[str, Any] = Field(default_factory=dict)


class CreateLogStreamRequest(BaseModel):
    log_group: str
    name: str
    source_service: str | None = None
    resource_id: str | None = None


class PutLogRequest(BaseModel):
    log_group: str
    log_stream: str
    timestamp: datetime | None = None
    message: str | None = None
    event: dict[str, Any] | None = None


class PutMetricRequest(BaseModel):
    namespace: str
    metric_name: str
    resource_id: str | None = None
    value: float
    unit: str
    dimensions: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime | None = None

    @field_validator("unit")
    @classmethod
    def validate_unit(cls, value: str) -> str:
        if value not in SUPPORTED_UNITS:
            raise ValueError("Unsupported metric unit")
        return value

    @field_validator("dimensions")
    @classmethod
    def validate_dimensions(cls, value: dict[str, Any]) -> dict[str, Any]:
        if len(value) > 30:
            raise ValueError("Metrics support at most 30 dimensions")
        return value


class CreateEventBusRequest(BaseModel):
    name: str


class PutEventRequest(BaseModel):
    event_bus: str = "default"
    source: str
    detail_type: str
    resources: list[str] = Field(default_factory=list)
    detail: dict[str, Any]
    timestamp: datetime | None = None
    request_id: str | None = None


class CreateAlarmRequest(BaseModel):
    name: str
    namespace: str
    metric_name: str
    dimensions: dict[str, Any] = Field(default_factory=dict)
    statistic: str = "Sum"
    period_seconds: int = Field(default=60, ge=1)
    evaluation_periods: int = Field(default=1, ge=1)
    datapoints_to_alarm: int = Field(default=1, ge=1)
    comparison_operator: str
    threshold: float
    enabled: bool = True

    @field_validator("statistic")
    @classmethod
    def validate_statistic(cls, value: str) -> str:
        if value not in SUPPORTED_STATISTICS:
            raise ValueError("Unsupported statistic")
        return value

    @field_validator("comparison_operator")
    @classmethod
    def validate_comparison(cls, value: str) -> str:
        if value not in SUPPORTED_COMPARISONS:
            raise ValueError("Unsupported comparison operator")
        return value


class PutAuditEventRequest(BaseModel):
    request_id: str | None = None
    principal: str | None = None
    service: str
    action: str
    resource: str | None = None
    decision: str | None = None
    status: str | None = None
    error_code: str | None = None
    source_ip: str | None = None
    user_agent: str | None = None
    timestamp: datetime | None = None
    detail: dict[str, Any] = Field(default_factory=dict)


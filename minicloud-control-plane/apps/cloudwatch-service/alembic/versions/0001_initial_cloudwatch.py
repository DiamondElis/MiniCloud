"""initial cloudwatch schema

Revision ID: 0001_initial_cloudwatch
Revises:
Create Date: 2026-05-19
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_cloudwatch"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

JSONB = postgresql.JSONB(astext_type=sa.Text())


def upgrade() -> None:
    op.create_table(
        "log_groups",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False, unique=True),
        sa.Column("retention_days", sa.Integer(), nullable=True),
        sa.Column("kms_key_id", sa.Text(), nullable=True),
        sa.Column("tags", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "log_streams",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("log_group_id", sa.String(36), sa.ForeignKey("log_groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("source_service", sa.Text(), nullable=True),
        sa.Column("resource_id", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("log_group_id", "name", name="uq_log_stream_group_name"),
    )
    op.create_table(
        "log_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("log_group_id", sa.String(36), sa.ForeignKey("log_groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("log_stream_id", sa.String(36), sa.ForeignKey("log_streams.id", ondelete="CASCADE"), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ingestion_time", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("event", JSONB, nullable=True),
        sa.Column("request_id", sa.Text(), nullable=True),
        sa.Column("principal", sa.Text(), nullable=True),
        sa.Column("service", sa.Text(), nullable=True),
        sa.Column("action", sa.Text(), nullable=True),
        sa.Column("resource", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=True),
        sa.Column("level", sa.Text(), nullable=False, server_default="INFO"),
    )
    op.create_table(
        "metric_datapoints",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("namespace", sa.Text(), nullable=False),
        sa.Column("metric_name", sa.Text(), nullable=False),
        sa.Column("dimensions", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("resource_id", sa.Text(), nullable=True),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.Text(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ingestion_time", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "event_buses",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("event_bus_id", sa.String(36), sa.ForeignKey("event_buses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("detail_type", sa.Text(), nullable=False),
        sa.Column("detail", JSONB, nullable=False),
        sa.Column("resources", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("request_id", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "alarm_definitions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False, unique=True),
        sa.Column("namespace", sa.Text(), nullable=False),
        sa.Column("metric_name", sa.Text(), nullable=False),
        sa.Column("dimensions", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("statistic", sa.Text(), nullable=False, server_default="Sum"),
        sa.Column("period_seconds", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("evaluation_periods", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("datapoints_to_alarm", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("comparison_operator", sa.Text(), nullable=False),
        sa.Column("threshold", sa.Float(), nullable=False),
        sa.Column("state", sa.Text(), nullable=False, server_default="INSUFFICIENT_DATA"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "alarm_state_history",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("alarm_id", sa.String(36), sa.ForeignKey("alarm_definitions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("old_state", sa.Text(), nullable=True),
        sa.Column("new_state", sa.Text(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("evaluated_value", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("request_id", sa.Text(), nullable=True),
        sa.Column("principal", sa.Text(), nullable=True),
        sa.Column("service", sa.Text(), nullable=False),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("resource", sa.Text(), nullable=True),
        sa.Column("decision", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=True),
        sa.Column("error_code", sa.Text(), nullable=True),
        sa.Column("source_ip", sa.Text(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("detail", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("ingestion_time", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    event_buses = sa.table("event_buses", sa.column("id", sa.String), sa.column("name", sa.String))
    op.bulk_insert(event_buses, [{"id": "default-bus", "name": "default"}, {"id": "security-bus", "name": "security"}, {"id": "platform-bus", "name": "platform"}])


def downgrade() -> None:
    for table in [
        "audit_events",
        "alarm_state_history",
        "alarm_definitions",
        "events",
        "event_buses",
        "metric_datapoints",
        "log_events",
        "log_streams",
        "log_groups",
    ]:
        op.drop_table(table)


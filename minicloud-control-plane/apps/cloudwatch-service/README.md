# MiniCloud CloudWatch Service

MiniCloud CloudWatch is the observability and event backbone for MiniCloud. It stores logs, metrics, events, alarms, and normalized audit activity for future services such as EC2, S3, VPC, RDS, WAF, GuardDuty, and the dashboard.

## Run Locally

From `minicloud-control-plane`:

```bash
docker compose -f infra/docker-compose.yml up --build
```

Run migrations:

```bash
cd apps/cloudwatch-service
DATABASE_URL=postgresql+psycopg://minicloud:minicloud@localhost:5433/minicloud_cloudwatch alembic upgrade head
```

Run tests:

```bash
cd apps/cloudwatch-service
pytest
```

## Example Commands

Create a log group:

```bash
curl -X POST http://localhost:8002/cloudwatch/log-groups \
  -H 'Content-Type: application/json' \
  -d '{"name":"MiniCloud/EC2","retention_days":30,"tags":{"service":"ec2","environment":"dev"}}'
```

Create a log stream:

```bash
curl -X POST http://localhost:8002/cloudwatch/log-streams \
  -H 'Content-Type: application/json' \
  -d '{"log_group":"MiniCloud/EC2","name":"instances","source_service":"ec2"}'
```

Put a structured log:

```bash
curl -X POST http://localhost:8002/cloudwatch/logs \
  -H 'Content-Type: application/json' \
  -d '{"log_group":"MiniCloud/EC2","log_stream":"instances","event":{"event_name":"RunInstance","instance_id":"i-abc123","principal":"user/elhan","service":"ec2","action":"ec2:RunInstance","status":"Success","request_id":"req-9f31a2"}}'
```

Query logs:

```bash
curl 'http://localhost:8002/cloudwatch/logs?log_group=MiniCloud/EC2&service=ec2'
```

Put a metric:

```bash
curl -X POST http://localhost:8002/cloudwatch/metrics \
  -H 'Content-Type: application/json' \
  -d '{"namespace":"MiniCloud/EC2","metric_name":"InstanceCreated","resource_id":"i-abc123","value":1,"unit":"Count","dimensions":{"InstanceType":"mini.t1","SubnetId":"subnet-123"}}'
```

Query metrics:

```bash
curl 'http://localhost:8002/cloudwatch/metrics?namespace=MiniCloud/EC2&metric_name=InstanceCreated'
```

Create an alarm:

```bash
curl -X POST http://localhost:8002/cloudwatch/alarms \
  -H 'Content-Type: application/json' \
  -d '{"name":"ec2-failed-launches-high","namespace":"MiniCloud/EC2","metric_name":"FailedLaunches","statistic":"Sum","period_seconds":300,"evaluation_periods":1,"datapoints_to_alarm":1,"comparison_operator":"GreaterThanThreshold","threshold":5,"dimensions":{"Service":"ec2"}}'
```

Evaluate an alarm:

```bash
curl -X POST http://localhost:8002/cloudwatch/alarms/ec2-failed-launches-high/evaluate
```

Put an audit event:

```bash
curl -X POST http://localhost:8002/cloudwatch/audit-events \
  -H 'Content-Type: application/json' \
  -d '{"request_id":"req-9f31a2","principal":"user/elhan","service":"ec2","action":"ec2:RunInstance","resource":"instance/i-abc123","decision":"Allow","status":"Success","detail":{"image":"nginx:latest","subnet_id":"subnet-123"}}'
```

## Example EC2 Integration

After `RunInstance`, EC2 would send:

```bash
curl -X POST http://cloudwatch-service:8002/cloudwatch/logs -H 'Content-Type: application/json' -d '{"log_group":"MiniCloud/EC2","log_stream":"instances","event":{"event_name":"RunInstance","instance_id":"i-abc123","principal":"user/elhan","service":"ec2","action":"ec2:RunInstance","status":"Success","request_id":"req-9f31a2"}}'
curl -X POST http://cloudwatch-service:8002/cloudwatch/metrics -H 'Content-Type: application/json' -d '{"namespace":"MiniCloud/EC2","metric_name":"InstanceCreated","resource_id":"i-abc123","value":1,"unit":"Count","dimensions":{"InstanceType":"mini.t1"}}'
curl -X POST http://cloudwatch-service:8002/cloudwatch/events -H 'Content-Type: application/json' -d '{"event_bus":"default","source":"minicloud.ec2","detail_type":"EC2 Instance State Change","resources":["instance/i-abc123"],"detail":{"previous_state":"pending","state":"running"},"request_id":"req-9f31a2"}'
curl -X POST http://cloudwatch-service:8002/cloudwatch/audit-events -H 'Content-Type: application/json' -d '{"request_id":"req-9f31a2","principal":"user/elhan","service":"ec2","action":"ec2:RunInstance","resource":"instance/i-abc123","decision":"Allow","status":"Success"}'
```

## Known Limitations

- No high-volume log storage yet.
- No distributed queue yet.
- No full EventBridge rules or targets yet.
- No CloudWatch dashboard yet.
- No OpenTelemetry ingestion yet.
- No long-term S3 archive yet.
- No TimescaleDB, Loki, or Prometheus backend yet.
- IAM integration supports local dev and mocked strict-mode tests first.

## Next Recommended Task

Integrate IAM and CloudWatch through the API Gateway so every MiniCloud API call gets a request ID, calls IAM authorization, and writes a normalized CloudWatch audit event.


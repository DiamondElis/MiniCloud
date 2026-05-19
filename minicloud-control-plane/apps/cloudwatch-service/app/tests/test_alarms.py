from sqlalchemy import select

from app.models.alarm import AlarmStateHistory
from app.models.event import Event


def create_alarm(client, threshold=5, metric="FailedLaunches"):
    response = client.post(
        "/cloudwatch/alarms",
        json={
            "name": "ec2-failed-launches-high",
            "namespace": "MiniCloud/EC2",
            "metric_name": metric,
            "statistic": "Sum",
            "period_seconds": 300,
            "evaluation_periods": 1,
            "datapoints_to_alarm": 1,
            "comparison_operator": "GreaterThanThreshold",
            "threshold": threshold,
            "dimensions": {"Service": "ec2"},
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def put_metric(client, value, metric="FailedLaunches"):
    return client.post(
        "/cloudwatch/metrics",
        json={"namespace": "MiniCloud/EC2", "metric_name": metric, "value": value, "unit": "Count", "dimensions": {"Service": "ec2"}},
    )


def test_create_alarm_starts_insufficient_data(client):
    alarm = create_alarm(client)
    assert alarm["state"] == "INSUFFICIENT_DATA"


def test_evaluate_alarm_with_no_datapoints_returns_insufficient_data(client):
    create_alarm(client)
    response = client.post("/cloudwatch/alarms/ec2-failed-launches-high/evaluate")
    assert response.json()["new_state"] == "INSUFFICIENT_DATA"


def test_evaluate_alarm_below_threshold_returns_ok(client):
    create_alarm(client)
    put_metric(client, 2)
    response = client.post("/cloudwatch/alarms/ec2-failed-launches-high/evaluate")
    assert response.json()["new_state"] == "OK"


def test_evaluate_alarm_above_threshold_returns_alarm(client):
    create_alarm(client)
    put_metric(client, 7)
    response = client.post("/cloudwatch/alarms/ec2-failed-launches-high/evaluate")
    assert response.json()["new_state"] == "ALARM"


def test_alarm_state_change_writes_history(client, db_session):
    create_alarm(client)
    put_metric(client, 7)
    rows = db_session.execute(select(AlarmStateHistory)).scalars().all()
    assert rows
    assert rows[-1].new_state == "ALARM"


def test_metric_ingestion_triggers_alarm_evaluation(client):
    create_alarm(client)
    put_metric(client, 7)
    response = client.get("/cloudwatch/alarms/ec2-failed-launches-high")
    assert response.json()["state"] == "ALARM"


def test_alarm_state_change_emits_platform_event(client, db_session):
    create_alarm(client)
    put_metric(client, 7)
    events = db_session.execute(select(Event).where(Event.detail_type == "CloudWatch Alarm State Change")).scalars().all()
    assert events


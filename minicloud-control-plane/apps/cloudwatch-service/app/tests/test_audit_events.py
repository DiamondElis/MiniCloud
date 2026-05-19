from sqlalchemy import select

from app.models.audit_event import AuditEvent


def test_put_audit_event_succeeds(client):
    response = client.post(
        "/cloudwatch/audit-events",
        json={"request_id": "req-1", "principal": "user/elhan", "service": "ec2", "action": "ec2:RunInstance", "status": "Success"},
    )
    assert response.status_code == 200
    assert response.json()["request_id"] == "req-1"


def test_query_audit_events_by_service_action_status_works(client):
    client.post("/cloudwatch/audit-events", json={"service": "ec2", "action": "ec2:RunInstance", "status": "Success"})
    response = client.get("/cloudwatch/audit-events?service=ec2&action=ec2:RunInstance&status=Success")
    assert len(response.json()) == 1


def test_every_non_audit_endpoint_writes_audit_event(client, db_session):
    client.post("/cloudwatch/log-groups", json={"name": "MiniCloud/EC2"})
    events = db_session.execute(select(AuditEvent).where(AuditEvent.service == "cloudwatch")).scalars().all()
    assert len(events) == 1
    assert events[0].action == "cloudwatch:CreateLogGroup"


def test_audit_write_endpoint_does_not_recurse_infinitely(client, db_session):
    client.post("/cloudwatch/audit-events", json={"service": "ec2", "action": "ec2:RunInstance"})
    events = db_session.execute(select(AuditEvent)).scalars().all()
    assert len(events) == 1
    assert events[0].service == "ec2"


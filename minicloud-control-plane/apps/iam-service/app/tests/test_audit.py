from sqlalchemy import select

from app.models.audit_event import AuditEvent
from app.tests.conftest import attach_user_policy, create_policy, create_user


def test_denied_decisions_are_logged(client, db_session):
    user = create_user(client)

    client.post("/iam/authorize", json={"principal_type": "user", "principal_id": user["id"], "action": "ec2:RunInstance", "resource": "*"})

    event = db_session.execute(select(AuditEvent)).scalar_one()
    assert event.decision == "Deny"
    assert event.reason == "ImplicitDeny"


def test_allowed_decisions_are_logged(client, db_session):
    user = create_user(client)
    policy = create_policy(client, "allow", {"Statement": [{"Effect": "Allow", "Action": "ec2:*", "Resource": "*"}]})
    attach_user_policy(client, user["id"], policy["id"])

    client.post("/iam/authorize", json={"principal_type": "user", "principal_id": user["id"], "action": "ec2:RunInstance", "resource": "*"})

    event = db_session.execute(select(AuditEvent)).scalar_one()
    assert event.decision == "Allow"
    assert event.reason == "ExplicitAllow"


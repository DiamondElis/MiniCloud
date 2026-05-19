from sqlalchemy import select

from app.models.audit_event import AuditEvent
from app.tests.conftest import attach_user_policy, create_policy, create_user


def authz(client, user_id, action="ec2:RunInstance", resource="instance/i-123"):
    return client.post(
        "/iam/authorize",
        json={"principal_type": "user", "principal_id": user_id, "action": action, "resource": resource},
    )


def test_no_policies_results_in_implicit_deny(client):
    user = create_user(client)

    response = authz(client, user["id"])

    assert response.json()["decision"] == "Deny"
    assert response.json()["reason"] == "ImplicitDeny"


def test_matching_allow_results_in_allow(client):
    user = create_user(client)
    policy = create_policy(client, "allow", {"Statement": [{"Effect": "Allow", "Action": "ec2:RunInstance", "Resource": "*"}]})
    attach_user_policy(client, user["id"], policy["id"])

    response = authz(client, user["id"])

    assert response.json()["decision"] == "Allow"
    assert response.json()["reason"] == "ExplicitAllow"


def test_matching_deny_overrides_allow(client):
    user = create_user(client)
    policy = create_policy(
        client,
        "mixed",
        {
            "Statement": [
                {"Effect": "Allow", "Action": "ec2:*", "Resource": "*"},
                {"Effect": "Deny", "Action": "ec2:RunInstance", "Resource": "*"},
            ]
        },
    )
    attach_user_policy(client, user["id"], policy["id"])

    response = authz(client, user["id"])

    assert response.json()["decision"] == "Deny"
    assert response.json()["reason"] == "ExplicitDeny"


def test_wildcard_action_matches(client):
    user = create_user(client)
    policy = create_policy(client, "ec2-all", {"Statement": [{"Effect": "Allow", "Action": "ec2:*", "Resource": "*"}]})
    attach_user_policy(client, user["id"], policy["id"])

    assert authz(client, user["id"], "ec2:RunInstance").json()["decision"] == "Allow"


def test_wildcard_resource_matches(client):
    user = create_user(client)
    policy = create_policy(client, "subnets", {"Statement": [{"Effect": "Allow", "Action": "ec2:AttachSubnet", "Resource": "subnet/*"}]})
    attach_user_policy(client, user["id"], policy["id"])

    response = authz(client, user["id"], "ec2:AttachSubnet", "subnet/subnet-123")

    assert response.json()["decision"] == "Allow"


def test_group_attached_policy_applies_to_user(client):
    user = create_user(client)
    group = client.post("/iam/groups", json={"name": "cloud-admins"}).json()
    assert client.post(f"/iam/groups/{group['id']}/users/{user['id']}").status_code == 204
    policy = create_policy(client, "group-allow", {"Statement": [{"Effect": "Allow", "Action": "s3:Get*", "Resource": "bucket/*"}]})
    assert client.post(f"/iam/groups/{group['id']}/policies", json={"policy_id": policy["id"]}).status_code == 204

    response = authz(client, user["id"], "s3:GetObject", "bucket/logs")

    assert response.json()["decision"] == "Allow"


def test_every_authorize_call_writes_audit_event(client, db_session):
    user = create_user(client)

    authz(client, user["id"])

    events = db_session.execute(select(AuditEvent)).scalars().all()
    assert len(events) == 1
    assert events[0].decision == "Deny"


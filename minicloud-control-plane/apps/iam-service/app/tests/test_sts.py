from app.tests.conftest import attach_user_policy, create_policy, create_user, login


def test_caller_with_permission_can_assume_role(client):
    user = create_user(client)
    token = login(client)
    role = client.post("/iam/roles", json={"name": "developer-admin"}).json()
    policy = create_policy(client, "assume-role", {"Statement": [{"Effect": "Allow", "Action": "sts:AssumeRole", "Resource": f"role/{role['id']}"}]})
    attach_user_policy(client, user["id"], policy["id"])

    response = client.post(
        "/sts/assume-role",
        json={"role_id": role["id"], "session_name": "demo-session", "duration_seconds": 3600},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["assumed_role"] == "developer-admin"
    assert response.json()["session_token"]


def test_caller_without_permission_cannot_assume_role(client):
    create_user(client)
    token = login(client)
    role = client.post("/iam/roles", json={"name": "developer-admin"}).json()

    response = client.post(
        "/sts/assume-role",
        json={"role_id": role["id"], "session_name": "demo-session", "duration_seconds": 3600},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_temporary_role_identity_works_with_get_caller_identity(client):
    user = create_user(client)
    token = login(client)
    role = client.post("/iam/roles", json={"name": "developer-admin"}).json()
    policy = create_policy(client, "assume-role", {"Statement": [{"Effect": "Allow", "Action": "sts:AssumeRole", "Resource": f"role/{role['id']}"}]})
    attach_user_policy(client, user["id"], policy["id"])
    assumed = client.post(
        "/sts/assume-role",
        json={"role_id": role["id"], "session_name": "demo-session", "duration_seconds": 3600},
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    response = client.get("/sts/get-caller-identity", headers={"Authorization": f"Bearer {assumed['session_token']}"})

    assert response.status_code == 200
    assert response.json()["principal_type"] == "role"
    assert response.json()["arn"] == "minicloud:iam::local:role/developer-admin"


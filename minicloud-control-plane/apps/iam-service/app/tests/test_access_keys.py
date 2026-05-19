from app.tests.conftest import create_user


def test_create_access_key_returns_secret_once(client):
    user = create_user(client)

    response = client.post("/iam/access-keys", json={"principal_type": "user", "principal_id": user["id"]})

    assert response.status_code == 200
    body = response.json()
    assert body["access_key_id"].startswith("MCAKIA")
    assert body["secret_access_key"].startswith("mcsk_live_")


def test_login_with_access_key_works(client):
    user = create_user(client)
    key = client.post("/iam/access-keys", json={"principal_type": "user", "principal_id": user["id"]}).json()

    response = client.post(
        "/iam/token",
        json={
            "grant_type": "access_key",
            "access_key_id": key["access_key_id"],
            "secret_access_key": key["secret_access_key"],
        },
    )

    assert response.status_code == 200
    assert response.json()["access_token"]


def test_disabled_key_fails(client):
    user = create_user(client)
    key = client.post("/iam/access-keys", json={"principal_type": "user", "principal_id": user["id"]}).json()
    assert client.patch(f"/iam/access-keys/{key['access_key_id']}", json={"status": "inactive"}).status_code == 200

    response = client.post(
        "/iam/token",
        json={
            "grant_type": "access_key",
            "access_key_id": key["access_key_id"],
            "secret_access_key": key["secret_access_key"],
        },
    )

    assert response.status_code == 401


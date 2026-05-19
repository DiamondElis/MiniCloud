from app.tests.conftest import create_user, login


def test_valid_password_returns_jwt(client):
    create_user(client)

    response = client.post("/iam/token", json={"grant_type": "password", "username": "elhan", "password": "password"})

    assert response.status_code == 200
    assert response.json()["token_type"] == "Bearer"
    assert response.json()["access_token"]


def test_invalid_password_fails(client):
    create_user(client)

    response = client.post("/iam/token", json={"grant_type": "password", "username": "elhan", "password": "wrong"})

    assert response.status_code == 401


def test_whoami_works_with_jwt(client):
    user = create_user(client)
    token = login(client)

    response = client.get("/iam/whoami", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["principal_id"] == user["id"]
    assert response.json()["username"] == "elhan"


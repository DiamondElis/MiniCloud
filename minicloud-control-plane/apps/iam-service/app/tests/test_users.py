def test_can_create_user(client):
    response = client.post("/iam/users", json={"username": "elhan", "email": "elhan@example.com", "password": "password"})

    assert response.status_code == 200
    assert response.json()["username"] == "elhan"
    assert "password" not in response.text


def test_duplicate_username_fails(client):
    payload = {"username": "elhan", "password": "password"}
    assert client.post("/iam/users", json=payload).status_code == 200

    response = client.post("/iam/users", json=payload)

    assert response.status_code == 409


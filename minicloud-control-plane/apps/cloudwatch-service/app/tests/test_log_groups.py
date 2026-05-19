from app.tests.conftest import create_group


def test_create_log_group_succeeds(client):
    group = create_group(client)
    assert group["name"] == "MiniCloud/EC2"


def test_duplicate_log_group_returns_conflict(client):
    create_group(client)
    response = client.post("/cloudwatch/log-groups", json={"name": "MiniCloud/EC2"})
    assert response.status_code == 409


def test_get_log_groups_returns_created_group(client):
    create_group(client)
    response = client.get("/cloudwatch/log-groups")
    assert response.status_code == 200
    assert response.json()[0]["name"] == "MiniCloud/EC2"


def test_delete_log_group_succeeds(client):
    create_group(client)
    response = client.delete("/cloudwatch/log-groups/MiniCloud/EC2")
    assert response.status_code == 204


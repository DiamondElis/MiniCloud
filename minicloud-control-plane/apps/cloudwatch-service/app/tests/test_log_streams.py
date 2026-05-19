from app.tests.conftest import create_group, create_stream


def test_create_stream_under_existing_group_succeeds(client):
    create_group(client)
    stream = create_stream(client)
    assert stream["name"] == "instances"


def test_create_stream_under_missing_group_fails(client):
    response = client.post("/cloudwatch/log-streams", json={"log_group": "missing", "name": "instances"})
    assert response.status_code == 404


def test_duplicate_stream_under_same_group_returns_conflict(client):
    create_group(client)
    create_stream(client)
    response = client.post("/cloudwatch/log-streams", json={"log_group": "MiniCloud/EC2", "name": "instances"})
    assert response.status_code == 409


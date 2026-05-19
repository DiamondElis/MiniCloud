from app.tests.conftest import create_group, create_stream


def setup_logs(client):
    create_group(client)
    create_stream(client)


def test_put_log_event_succeeds_for_existing_group_stream(client):
    setup_logs(client)
    response = client.post("/cloudwatch/logs", json={"log_group": "MiniCloud/EC2", "log_stream": "instances", "message": "hello"})
    assert response.status_code == 200
    assert response.json()["message"] == "hello"


def test_put_log_event_extracts_common_fields(client):
    setup_logs(client)
    event = {"request_id": "req-1", "principal": "user/elhan", "service": "ec2", "action": "ec2:RunInstance", "status": "Success"}
    response = client.post("/cloudwatch/logs", json={"log_group": "MiniCloud/EC2", "log_stream": "instances", "event": event})
    body = response.json()
    assert body["request_id"] == "req-1"
    assert body["principal"] == "user/elhan"
    assert body["service"] == "ec2"
    assert body["action"] == "ec2:RunInstance"
    assert body["status"] == "Success"


def test_put_log_event_uses_server_time_if_timestamp_omitted(client):
    setup_logs(client)
    response = client.post("/cloudwatch/logs", json={"log_group": "MiniCloud/EC2", "log_stream": "instances", "message": "hello"})
    assert response.json()["timestamp"]


def test_query_logs_by_group_works(client):
    setup_logs(client)
    client.post("/cloudwatch/logs", json={"log_group": "MiniCloud/EC2", "log_stream": "instances", "message": "hello"})
    response = client.get("/cloudwatch/logs?log_group=MiniCloud/EC2")
    assert len(response.json()) == 1


def test_query_logs_by_service_works(client):
    setup_logs(client)
    client.post("/cloudwatch/logs", json={"log_group": "MiniCloud/EC2", "log_stream": "instances", "event": {"service": "ec2"}})
    response = client.get("/cloudwatch/logs?service=ec2")
    assert len(response.json()) == 1


def test_missing_group_or_stream_fails(client):
    assert client.post("/cloudwatch/logs", json={"log_group": "missing", "log_stream": "instances"}).status_code == 404
    create_group(client)
    assert client.post("/cloudwatch/logs", json={"log_group": "MiniCloud/EC2", "log_stream": "missing"}).status_code == 404


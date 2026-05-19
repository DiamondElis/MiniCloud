def test_default_event_bus_is_seeded(client):
    response = client.get("/cloudwatch/event-buses")
    names = {bus["name"] for bus in response.json()}
    assert {"default", "security", "platform"}.issubset(names)


def test_put_event_to_default_bus_succeeds(client):
    response = client.post("/cloudwatch/events", json={"source": "minicloud.ec2", "detail_type": "EC2 State", "detail": {"state": "running"}})
    assert response.status_code == 200
    assert response.json()["source"] == "minicloud.ec2"


def test_put_event_to_missing_bus_fails(client):
    response = client.post("/cloudwatch/events", json={"event_bus": "missing", "source": "minicloud.ec2", "detail_type": "EC2 State", "detail": {}})
    assert response.status_code == 404


def test_query_events_by_source_works(client):
    client.post("/cloudwatch/events", json={"source": "minicloud.ec2", "detail_type": "EC2 State", "detail": {}})
    response = client.get("/cloudwatch/events?source=minicloud.ec2")
    assert len(response.json()) == 1


def test_query_events_by_detail_type_works(client):
    client.post("/cloudwatch/events", json={"source": "minicloud.ec2", "detail_type": "EC2 Instance State Change", "detail": {}})
    response = client.get("/cloudwatch/events?detail_type=EC2 Instance State Change")
    assert len(response.json()) == 1


def put_metric(client, value=1, unit="Count", dimensions=None, name="InstanceCreated"):
    return client.post(
        "/cloudwatch/metrics",
        json={
            "namespace": "MiniCloud/EC2",
            "metric_name": name,
            "value": value,
            "unit": unit,
            "dimensions": dimensions or {"Service": "ec2"},
        },
    )


def test_put_metric_succeeds(client):
    response = put_metric(client)
    assert response.status_code == 200
    assert response.json()["value"] == 1


def test_invalid_unit_fails(client):
    assert put_metric(client, unit="Bananas").status_code == 422


def test_non_numeric_value_fails(client):
    response = client.post("/cloudwatch/metrics", json={"namespace": "MiniCloud/EC2", "metric_name": "M", "value": "x", "unit": "Count"})
    assert response.status_code == 422


def test_more_than_30_dimensions_fails(client):
    dims = {f"K{i}": i for i in range(31)}
    assert put_metric(client, dimensions=dims).status_code == 422


def test_query_metrics_by_namespace_and_metric_name_works(client):
    put_metric(client)
    response = client.get("/cloudwatch/metrics?namespace=MiniCloud/EC2&metric_name=InstanceCreated")
    assert len(response.json()) == 1


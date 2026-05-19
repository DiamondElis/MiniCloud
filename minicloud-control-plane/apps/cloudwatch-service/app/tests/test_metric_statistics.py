def put(client, value):
    response = client.post("/cloudwatch/metrics", json={"namespace": "MiniCloud/EC2", "metric_name": "CPUUtilization", "value": value, "unit": "Percent"})
    assert response.status_code == 200


def stat(client, statistic):
    response = client.get(f"/cloudwatch/metrics/statistics?namespace=MiniCloud/EC2&metric_name=CPUUtilization&period=60&statistic={statistic}")
    assert response.status_code == 200
    return response.json()


def test_metric_statistics_sum_works(client):
    put(client, 2)
    put(client, 3)
    assert stat(client, "Sum")["value"] == 5


def test_metric_statistics_average_works(client):
    put(client, 2)
    put(client, 4)
    assert stat(client, "Average")["value"] == 3


def test_metric_statistics_count_works(client):
    put(client, 2)
    put(client, 4)
    assert stat(client, "Count")["value"] == 2


def test_metric_statistics_minimum_and_maximum_work(client):
    put(client, 2)
    put(client, 4)
    assert stat(client, "Minimum")["value"] == 2
    assert stat(client, "Maximum")["value"] == 4


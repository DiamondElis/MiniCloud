def test_iam_auth_disabled_requests_succeed_as_dev_principal(client):
    response = client.post("/cloudwatch/log-groups", json={"name": "MiniCloud/EC2"})
    assert response.status_code == 200
    audit = client.get("/cloudwatch/audit-events").json()[0]
    assert audit["principal"] == "system/dev"


def test_iam_auth_enabled_and_iam_denies_returns_403(client, strict_auth):
    strict_auth(client, allowed=False)
    response = client.post("/cloudwatch/log-groups", json={"name": "MiniCloud/EC2"}, headers={"Authorization": "Bearer token"})
    assert response.status_code == 403


def test_iam_auth_enabled_and_iam_allows_succeeds(client, strict_auth):
    strict_auth(client, allowed=True)
    response = client.post("/cloudwatch/log-groups", json={"name": "MiniCloud/EC2"}, headers={"Authorization": "Bearer token"})
    assert response.status_code == 200


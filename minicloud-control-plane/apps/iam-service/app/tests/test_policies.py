from app.tests.conftest import create_policy


def test_valid_policy_stores(client, valid_policy_doc):
    policy = create_policy(client, "ec2-run", valid_policy_doc)

    assert policy["name"] == "ec2-run"
    assert policy["document"]["Statement"][0]["Effect"] == "Allow"


def test_invalid_effect_fails(client, valid_policy_doc):
    valid_policy_doc["Statement"][0]["Effect"] = "Maybe"

    response = client.post("/iam/policies", json={"name": "bad", "document": valid_policy_doc})

    assert response.status_code == 422


def test_missing_action_fails(client, valid_policy_doc):
    valid_policy_doc["Statement"][0].pop("Action")

    response = client.post("/iam/policies", json={"name": "bad", "document": valid_policy_doc})

    assert response.status_code == 422


def test_missing_resource_fails(client, valid_policy_doc):
    valid_policy_doc["Statement"][0].pop("Resource")

    response = client.post("/iam/policies", json={"name": "bad", "document": valid_policy_doc})

    assert response.status_code == 422


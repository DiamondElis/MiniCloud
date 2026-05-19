import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app import models  # noqa: F401


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    app = create_app()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture()
def valid_policy_doc() -> dict:
    return {
        "Version": "2026-01-01",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["ec2:RunInstance"],
                "Resource": "*",
            }
        ],
    }


def create_user(client: TestClient, username: str = "elhan", password: str = "password") -> dict:
    response = client.post("/iam/users", json={"username": username, "password": password})
    assert response.status_code == 200, response.text
    return response.json()


def create_policy(client: TestClient, name: str, document: dict) -> dict:
    response = client.post("/iam/policies", json={"name": name, "document": document})
    assert response.status_code == 200, response.text
    return response.json()


def attach_user_policy(client: TestClient, user_id: str, policy_id: str) -> None:
    response = client.post(f"/iam/users/{user_id}/policies", json={"policy_id": policy_id})
    assert response.status_code == 204, response.text


def login(client: TestClient, username: str = "elhan", password: str = "password") -> str:
    response = client.post(
        "/iam/token",
        json={"grant_type": "password", "username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


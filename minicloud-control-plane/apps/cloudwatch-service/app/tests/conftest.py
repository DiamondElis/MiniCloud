from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.clients.iam_client import IamClient
from app.core.auth import get_iam_client
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.repositories.events_repo import seed_default_buses


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool, future=True)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = TestingSessionLocal()
    seed_default_buses(session)
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


def create_group(client: TestClient, name: str = "MiniCloud/EC2") -> dict:
    response = client.post("/cloudwatch/log-groups", json={"name": name, "retention_days": 30})
    assert response.status_code == 200, response.text
    return response.json()


def create_stream(client: TestClient, group: str = "MiniCloud/EC2", name: str = "instances") -> dict:
    response = client.post("/cloudwatch/log-streams", json={"log_group": group, "name": name, "source_service": "ec2"})
    assert response.status_code == 200, response.text
    return response.json()


class FakeIamClient:
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed

    def whoami(self, token: str) -> dict:
        return {"principal_type": "user", "principal_id": "u-1"}

    def authorize(self, token: str, principal_type: str, principal_id: str, action: str, resource: str) -> bool:
        return self.allowed


@pytest.fixture()
def strict_auth(monkeypatch):
    import app.core.auth as auth_module

    def apply(client: TestClient, allowed: bool) -> None:
        monkeypatch.setattr(auth_module, "get_settings", lambda: SimpleNamespace(iam_auth_enabled=True, iam_base_url="http://iam"))
        client.app.dependency_overrides[get_iam_client] = lambda: FakeIamClient(allowed)

    return apply


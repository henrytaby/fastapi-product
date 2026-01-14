import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.core.db import get_session
from app.main import app

# Import all models to ensure metadata is populated for creation

# ... import other models as needed


@pytest.fixture(name="session")
def session_fixture():
    # Use in-memory SQLite for tests
    # Use in-memory SQLite for tests
    test_engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(test_engine)
    
    # Patch global engine
    from app.core import db
    db.engine = test_engine
    
    # Also register hooks manually here since lifespan might have run with old engine 
    # (though hooks are on Session class, so it's fine)
    from app.core.audit_hooks import register_audit_hooks
    register_audit_hooks(test_engine)

    with Session(test_engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="superuser")
def superuser_fixture(session: Session):
    from app.models.user import User
    from app.auth.utils import get_password_hash
    
    user = User(
        username="superuser",
        email="superuser@example.com",
        password_hash=get_password_hash("password"),
        is_superuser=True,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="superuser_token_headers")
def superuser_token_headers_fixture(client: TestClient, superuser):
    return get_authorization_headers(client, superuser.username, "password")


def get_authorization_headers(client: TestClient, username: str, password: str) -> dict:
    login_data = {
        "username": username,
        "password": password,
    }
    r = client.post("/api/auth/token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers

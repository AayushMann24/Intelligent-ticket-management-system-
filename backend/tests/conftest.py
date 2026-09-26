import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.connection import get_db
from app.main import app
from app.config import settings
from app.utils.security import hash_password

from fastapi.testclient import TestClient


# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Global variable to hold the current test session
_current_test_session = None


def override_get_db():
    if _current_test_session is not None:
        yield _current_test_session
    else:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()


@pytest.fixture(scope="function")
def db_session():
    global _current_test_session
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    _current_test_session = db
    try:
        yield db
    finally:
        _current_test_session = None
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    from app.models.user import User
    user = User(
        name="Test User",
        email="test@example.com",
        password=hash_password("testpassword123"),
        role="Employee",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session):
    from app.models.user import User
    user = User(
        name="Admin User",
        email="admin@example.com",
        password=hash_password("adminpassword123"),
        role="Admin",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def technician_user(db_session):
    from app.models.user import User
    user = User(
        name="Tech User",
        email="tech@example.com",
        password=hash_password("techpassword123"),
        role="Technician",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user):
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "testpassword123",
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(client, admin_user):
    response = client.post("/auth/login", json={
        "email": "admin@example.com",
        "password": "adminpassword123",
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def tech_auth_headers(client, technician_user):
    response = client.post("/auth/login", json={
        "email": "tech@example.com",
        "password": "techpassword123",
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
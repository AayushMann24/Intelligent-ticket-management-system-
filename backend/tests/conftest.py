import os
import pytest
from unittest.mock import patch
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Set test environment variables BEFORE importing app modules
# This ensures the Settings object picks up the test database URL
os.environ.setdefault("DATABASE_URL", "postgresql://test_user:test_pass@localhost:5433/itms_test")
os.environ.setdefault("SECRET_KEY", "test_secret_key_not_for_production_use_only")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")
os.environ.setdefault("SLA_MONITOR_ENABLED", "false")
os.environ.setdefault("COOKIE_SECURE", "false")
os.environ.setdefault("HSTS_ENABLED", "false")
os.environ.setdefault("CSP_ENABLED", "true")
os.environ.setdefault("SECURITY_HEADERS_ENABLED", "true")

from app.database.base import Base
from app.database.connection import get_db
from app.main import app
from app.config import settings
from app.utils.security import hash_password
from app.utils.rate_limiter import rate_limiter

from fastapi.testclient import TestClient


# PostgreSQL test database engine
# Using NullPool to avoid connection pooling issues in tests
TEST_DATABASE_URL = settings.database_url

engine = create_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Track if alembic upgrade has been run in this process
_alembic_upgraded = False


def _run_alembic_upgrade():
    """
    Run alembic upgrade head against the test database.
    This initializes a fresh database with the complete migration chain.
    Idempotent: only runs once per process.
    """
    global _alembic_upgraded
    
    if _alembic_upgraded:
        return
    
    import subprocess
    import sys
    
    env = os.environ.copy()
    env["DATABASE_URL"] = TEST_DATABASE_URL
    
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=os.path.dirname(os.path.dirname(__file__)),
        env=env,
        capture_output=True,
        text=True,
    )
    
    if result.returncode != 0:
        # If the error is "already at head" or tables exist, that's OK
        stderr = result.stderr.lower()
        if "already at head" in stderr or "duplicate" in stderr or "already exists" in stderr:
            _alembic_upgraded = True
            return
        raise RuntimeError(f"Alembic upgrade failed:\n{result.stdout}\n{result.stderr}")
    
    _alembic_upgraded = True


def _verify_schema_exists():
    """Verify that the schema has been created by checking for key tables."""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename IN ('users', 'tickets', 'ticket_history')
        """))
        count = result.scalar()
        return count >= 3


@pytest.fixture(scope="session", autouse=True)
def initialize_test_db():
    """
    Session-scoped fixture that initializes the test database once per test session.
    Uses alembic upgrade head to create the complete schema from an empty database.
    Idempotent: safe to call multiple times.
    """
    # Run full migration chain on fresh database (idempotent)
    _run_alembic_upgrade()
    
    # Verify schema exists
    if not _verify_schema_exists():
        raise RuntimeError("Test database schema verification failed - tables not found")
    
    yield
    
    # No teardown - the test database persists for the session


@pytest.fixture(scope="function")
def db_connection(initialize_test_db):
    """
    Function-scoped fixture that provides a database connection with transaction rollback.
    Each test gets its own transaction that is rolled back after the test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    
    # Begin a nested transaction (savepoint) for the test
    # This allows the application to call commit() without actually committing
    nested = connection.begin_nested()
    
    # If the application calls session.commit(), it will commit to the nested transaction
    # We need to restart the savepoint after each commit
    def restart_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()
    
    event.listen(TestingSessionLocal, "after_transaction_end", restart_savepoint)
    
    try:
        yield connection
    finally:
        event.remove(TestingSessionLocal, "after_transaction_end", restart_savepoint)
        nested.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def db_session(db_connection):
    """
    Function-scoped fixture that provides a SQLAlchemy session bound to the test connection.
    """
    session = TestingSessionLocal(bind=db_connection)
    try:
        yield session
    finally:
        session.close()


# Global variable to hold the current test session (for dependency override)
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


@pytest.fixture(scope="session", autouse=True)
def disable_rate_limiting():
    """Disable rate limiting for all tests."""
    original_enabled = settings.rate_limit_enabled
    settings.rate_limit_enabled = False
    yield
    settings.rate_limit_enabled = original_enabled


@pytest.fixture(scope="function", autouse=True)
def reset_rate_limiter():
    """Reset rate limiter between tests."""
    yield
    import asyncio
    asyncio.run(rate_limiter.reset_all())


@pytest.fixture(scope="function", autouse=True)
def mock_ai_service():
    """
    Mock AI service to prevent external network calls to Ollama during tests.
    
    Returns deterministic AI analysis results that match the structure
    expected by ticket_service.create_ticket() -> build_ticket().
    
    This fixture is autouse because:
    - No tests explicitly test AI functionality
    - All ticket creation tests indirectly invoke the AI pipeline
    - CI does not run Ollama, causing connection refused errors
    - The production code already has a fallback for when AI is unavailable
    """
    def mock_analyze_ticket(title: str, description: str, technicians: list):
        return {
            "category": "Other",
            "subcategory": "General",
            "keywords": [],
            "confidence": 0.0,
            "priority": "Medium",
            "priority_reason": "Test mock priority",
            "assigned_to": None,
            "assignment_reason": "Test mock assignment",
        }
    
    def mock_dashboard_insights(dashboard_stats: dict):
        return {"summary": "Test mock insights", "details": {}}
    
    with patch("app.services.ai_service.AIService.analyze_ticket", side_effect=mock_analyze_ticket):
        with patch("app.services.ai_service.AIService.dashboard_insights", side_effect=mock_dashboard_insights):
            yield


@pytest.fixture(scope="function")
def client(db_session):
    """
    Function-scoped test client with database session override.
    """
    global _current_test_session
    _current_test_session = db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    _current_test_session = None


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
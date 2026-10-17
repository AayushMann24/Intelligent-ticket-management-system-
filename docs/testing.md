# Testing Guide

This document describes how to run the ITMS backend and frontend tests using the dedicated PostgreSQL test database.

## Overview

The test infrastructure uses a **dedicated PostgreSQL 16 test database** (`db_test` service) that is completely isolated from the development database (`db` service).

| Database | Service | Port | Volume | Purpose |
|----------|---------|------|--------|---------|
| Development | `db` | 5432 (internal) | `postgres_data` | Used by running backend/frontend containers |
| Test | `db_test` | **5433 (host)** → 5432 (container) | `postgres_test_data` | Used by `pytest` when running backend tests |

**Key point**: The test database runs on **port 5433** on the host to avoid conflicting with the development database on port 5432.

---

## Prerequisites

- Docker and Docker Compose installed
- Python 3.12+ with project dependencies installed (`pip install -r backend/requirements.txt`)
- Node.js 18+ with frontend dependencies installed (`npm install` in `frontend/`)

---

## Running Tests

### 1. Start the Test Database

```bash
docker compose --profile test up -d db_test
```

Wait for the health check to pass (usually 10-20 seconds):

```bash
docker compose ps
```

You should see `itms_postgres_test` with status `Up ... (healthy)`.

### 2. Run Backend Tests

```bash
cd backend
python -m pytest tests/ -v --tb=short
```

**Expected result**: 305 tests passing.

To run the escalation-administration tests only:

```bash
cd backend
python -m pytest tests/test_escalation.py -v
```

**Expected result**: 39 tests passing.

### 3. Run Frontend Tests

```bash
cd frontend
npm test
```

**Expected result**: 4 tests passing.

### 4. Run Frontend TypeScript/Build Check

```bash
cd frontend
npm run build
```

**Expected result**: Build succeeds (TypeScript compilation + Vite bundling).

---

## How It Works

### Backend Test Configuration

- **`backend/.env.test`**: Contains test-specific environment variables including:
  - `DATABASE_URL=postgresql://test_user:test_pass@localhost:5433/itms_test`
  - Test-only `SECRET_KEY`
  - Disabled rate limiting, SLA monitor, HSTS
  - Debug mode enabled

- **`backend/tests/conftest.py`**: Pytest configuration that:
  1. Sets test environment variables before importing app modules
  2. Creates a PostgreSQL SQLAlchemy engine pointing to `localhost:5433`
  3. **Initializes the test database once per session** by running the full
     Alembic migration chain (`alembic upgrade head`) against an empty database,
     so tests exercise the exact same schema (and seed data) as production
  4. **Provides transaction-based isolation per test**:
     - Each test gets a database connection with a transaction
     - Uses nested transactions (savepoints) to handle application `commit()` calls
     - Rolls back the transaction after each test — **no DROP/CREATE needed**

### Database Initialization

The test database is initialized by running the **Alembic migration chain from
base to head** (`alembic upgrade head`) once per test session. This means the
test schema — including enum types, foreign keys, indexes, and migration-seeded
data — matches the production migration head exactly.

Because the Phase 2D-4 migration seeds default escalation rules, those default
rules are present in the test database. Tests that assert exact rule counts or
matching results clear the table first (see the `_isolate_escalation_rules`
fixture in `tests/test_notifications.py`).

### Escalation tests and email delivery

`backend/tests/test_escalation.py` covers the escalation-administration API:

- Authorization (Admin-only rule management and record inspection)
- Rule CRUD, precedence/specificity, and idempotency
- Migration seeding presence, idempotency, and reversibility
- SMTP provider success/failure and configuration
- Regression: email transport failures never block the escalation workflow

**No test sends real email.** The default email provider is `mock`, and the SMTP
tests patch `smtplib.SMTP` so no network connection is made. The test
environment does not set `EMAIL_PROVIDER`, so it falls back to the safe `mock`
default.

After initialization, the test database is at revision:

```
phase2d4_escalation_defaults (head)
```

Verify with:

```bash
cd backend
DATABASE_URL=postgresql://test_user:test_pass@localhost:5433/itms_test python -m alembic current
```

---

### Troubleshooting

### Test Database Not Healthy

```bash
docker compose --profile test logs db_test
```

Common issues:
- Port 5433 already in use → Stop other PostgreSQL instances
- Container fails to start → Check Docker resources (memory, disk)

### Tests Fail to Connect to Database

Ensure:
1. `db_test` is healthy: `docker compose --profile test ps`
2. Port 5433 is accessible: `nc -zv localhost 5433`
3. Environment variables are set correctly (check `backend/.env.test`)

### Alembic Stamp Fails

If the test database already exists with a different schema:
```bash
docker compose --profile test down db_test
docker volume rm itms_postgres_test_data
docker compose --profile test up -d db_test
# Wait for healthy, then re-run tests
```

---

## CI/CD Integration

For GitHub Actions, GitLab CI, or similar:

```yaml
services:
  db_test:
    image: postgres:16-alpine
    env:
      POSTGRES_DB: itms_test
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_pass
    ports: ["5433:5432"]
    options: >-
      --health-cmd "pg_isready -U test_user"
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5

steps:
  - name: Start test database
    run: docker compose --profile test up -d db_test
  
  - name: Wait for database
    run: sleep 15 && docker compose --profile test ps
  
  - name: Run backend tests
    working-directory: backend
    env:
      DATABASE_URL: postgresql://test_user:test_pass@localhost:5433/itms_test
      SECRET_KEY: test_secret_key_for_ci_only
    run: python -m pytest tests/ -v --tb=short
```

---

## Isolation Guarantees

- **Test data never touches development database**: Separate container, separate volume, separate port
- **Tests don't affect each other**: Transaction rollback per test
- **Production containers unaffected**: `itms_postgres`, `itms_backend`, `itms_frontend` continue running
- **No manual cleanup needed**: Test database persists for the session; `docker compose down -v` removes everything if needed

---

## Common Commands Reference

```bash
# Start test DB only
docker compose --profile test up -d db_test

# Check status
docker compose --profile test ps

# View test DB logs
docker compose --profile test logs db_test

# Stop test DB
docker compose --profile test stop db_test

# Remove test DB and volume (full reset)
docker compose --profile test down db_test
docker volume rm itms_postgres_test_data

# Run backend tests
cd backend && python -m pytest tests/ -v --tb=short

# Run specific test file
cd backend && python -m pytest tests/test_tickets.py -v

# Run frontend tests
cd frontend && npm test

# Build frontend
cd frontend && npm run build

# Check Alembic status on test DB
cd backend && DATABASE_URL=postgresql://test_user:test_pass@localhost:5433/itms_test python -m alembic current
```
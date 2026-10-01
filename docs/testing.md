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
docker compose up -d db_test
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

**Expected result**: 103 tests passing.

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
  3. **Initializes the test database once per session**:
     - Creates all tables from SQLAlchemy models (`Base.metadata.create_all()`)
     - Stamps Alembic to the head revision (`phase2c2_sla_breach_events`)
  4. **Provides transaction-based isolation per test**:
     - Each test gets a database connection with a transaction
     - Uses nested transactions (savepoints) to handle application `commit()` calls
     - Rolls back the transaction after each test — **no DROP/CREATE needed**

### Database Initialization

The test database is initialized from the **current SQLAlchemy models** (not by running the full migration chain from scratch), because the existing Alembic migration chain assumes tables already exist (the first migration modifies existing tables rather than creating them).

This approach:
- ✅ Creates the exact same schema as production (models match migration head)
- ✅ Exercises PostgreSQL-specific features (enums, FKs, indexes, JSONB, timestamptz)
- ✅ Is fast (no per-test DDL)
- ✅ Tests the actual PostgreSQL behavior that matters

### Alembic Revision

After initialization, the test database is at revision:
```
phase2c2_sla_breach_events (head)
```

Verify with:
```bash
cd backend
DATABASE_URL=postgresql://test_user:test_pass@localhost:5433/itms_test python -m alembic current
```

---

## Troubleshooting

### Test Database Not Healthy

```bash
docker compose logs db_test
```

Common issues:
- Port 5433 already in use → Stop other PostgreSQL instances
- Container fails to start → Check Docker resources (memory, disk)

### Tests Fail to Connect to Database

Ensure:
1. `db_test` is healthy: `docker compose ps`
2. Port 5433 is accessible: `nc -zv localhost 5433`
3. Environment variables are set correctly (check `backend/.env.test`)

### Alembic Stamp Fails

If the test database already exists with a different schema:
```bash
docker compose down db_test
docker volume rm itms_postgres_test_data
docker compose up -d db_test
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
    run: docker compose up -d db_test
  
  - name: Wait for database
    run: sleep 15 && docker compose ps
  
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
docker compose up -d db_test

# Check status
docker compose ps

# View test DB logs
docker compose logs db_test

# Stop test DB
docker compose stop db_test

# Remove test DB and volume (full reset)
docker compose down db_test
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
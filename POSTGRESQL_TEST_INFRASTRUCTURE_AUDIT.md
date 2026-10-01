# ITMS — PHASE 2C-3C CHECKPOINT 1: PostgreSQL TEST INFRASTRUCTURE AUDIT + SAFE PLAN

---

## A. CURRENT TEST DATABASE

| Aspect | Details |
|--------|---------|
| **Database Engine** | **SQLite (in-memory)** — `sqlite:///:memory:` |
| **Connection Mechanism** | SQLAlchemy `create_engine` with `StaticPool` and `check_same_thread=False` |
| **Relevant Files** | `backend/tests/conftest.py` (lines 16-24, 60-70) |
| **Test Command** | `python -m pytest tests/ -v --tb=short` |
| **Actual Test Result** | **103 tests collected, 103 passed** (3 min 8 sec) |
| **Test Organization** | `backend/tests/` with 4 test modules: `test_auth.py` (32), `test_security_headers.py` (27), `test_tickets.py` (42), `test_users.py` (12) |
| **Test Isolation** | Per-function: `Base.metadata.create_all()` → yield session → `Base.metadata.drop_all()` |
| **Session Management** | Global `_current_test_session` variable + `override_get_db()` dependency override |
| **Fixtures** | `db_session`, `client`, `test_user`, `admin_user`, `technician_user`, `auth_headers`, `admin_auth_headers`, `tech_auth_headers` |

---

## B. PROBLEMS / RISKS

### 1. SQLite vs PostgreSQL Differences (Critical)
| Feature | SQLite (Test) | PostgreSQL (Production) | Risk |
|---------|---------------|------------------------|------|
| **Enum Type** | Stored as TEXT (no native enum) | Native `ENUM` type (`historyeventtype`) | **False positives**: Tests pass but enum constraints/values fail in PG |
| **JSON Type** | Stored as TEXT | Native `JSONB` | Query/index behavior differs |
| **Timestamp with TZ** | Stored as TEXT/INTEGER | Native `TIMESTAMPTZ` | Timezone handling, comparison bugs |
| **Foreign Keys** | Not enforced by default (PRAGMA required) | Enforced strictly | FK violations only caught in PG |
| **Indexes** | Basic B-tree | Partial, expression, GIN, BRIN | Query plans differ; missing index bugs |
| **Constraints** | Limited `CHECK`, no `EXCLUDE` | Full constraint support | Data integrity bugs slip through |
| **Concurrency** | Serialized (file lock) | MVCC | Race conditions, deadlocks invisible in tests |
| **ALTER TYPE** | N/A | `ADD VALUE IF NOT EXISTS` | Migration `phase2c2_sla_breach_events` uses PG-specific syntax |

### 2. Isolation Problems
- **Global session variable** (`_current_test_session`) is not thread-safe; risky if parallel test execution is added later.
- **`create_all`/`drop_all` per test** recreates schema from SQLAlchemy models, **not from Alembic migrations**. DDL drift possible.
- **No transaction rollback** — uses DROP/CREATE which is slow and doesn't test transaction semantics.

### 3. Migration Problems
- Tests **never run Alembic migrations**. They use `Base.metadata.create_all()` which:
  - Creates tables from current models only
  - Does not test migration chain `base → phase2c2_sla_breach_events`
  - Misses `ALTER TYPE ... ADD VALUE` statements (enum evolution)
  - Misses data migrations (e.g., `UPDATE tickets SET ticket_type = 'INCIDENT'`)
- **Enum evolution** (`historyeventtype`) tested only in PG via raw SQL in migrations — **untested in current suite**.

### 4. CI Limitations
- Current tests require only Python + SQLite — fast but **not representative**.
- No PostgreSQL service in CI pipeline defined.
- Testcontainers **not installed** (verified: not in requirements.txt, not referenced anywhere).

### 5. False-Positive Scenarios
| Scenario | Why It Passes in SQLite | Fails in PostgreSQL |
|----------|------------------------|---------------------|
| Enum value `SLA_RESPONSE_BREACHED` | TEXT column accepts any string | Enum type rejects unknown values |
| `JSON` column query `->>` operator | Not supported (TEXT) | Works natively |
| `ON DELETE CASCADE` FK | Not enforced | Enforced |
| Timezone-aware datetime comparison | String compare | Proper TZ compare |
| Concurrent writes | Serialized | MVCC conflicts |

---

## C. RECOMMENDED IMPLEMENTATION

### Chosen Strategy: **Option A — Dedicated PostgreSQL Test Service in Docker Compose**

**Why it fits ITMS architecture:**
- ✅ Already uses Docker Compose for dev stack (`docker-compose.yml` with `db` service)
- ✅ PostgreSQL 16 image already validated and healthy
- ✅ No new external dependencies (Testcontainers adds complexity, Docker is already required)
- ✅ Developers already run `docker compose up` — test DB is one more service
- ✅ Alembic migrations already target PostgreSQL (production schema)
- ✅ Works identically in CI/CD (GitHub Actions, GitLab CI, etc. support Docker services)
- ✅ Does not contaminate development database (separate container, separate volume)
- ✅ Supports isolated test runs (each test run gets fresh DB via `alembic upgrade head`)
- ✅ Minimal maintainable solution — reuses existing Docker, Alembic, and config patterns

### Exact Files That Would Need to Change

| File | Change Type | Description |
|------|-------------|-------------|
| `backend/tests/conftest.py` | **Major rewrite** | Replace SQLite engine with PostgreSQL test DB; use Alembic for schema; transaction-based rollback |
| `docker-compose.yml` | **Add service** | Add `db_test` service (PostgreSQL 16, separate volume, no port exposure needed) |
| `backend/.env.test` (new) | **New file** | Test-specific env vars: `DATABASE_URL=postgresql://...`, `SECRET_KEY=test`, etc. |
| `backend/pytest.ini` | **Minor** | Add `env_file = .env.test` or use `pytest-env` plugin |
| `backend/alembic/env.py` | **None** | Already reads `settings.database_url` — works if config points to test DB |
| `backend/app/config.py` | **None** | Already uses `BaseSettings` with `.env` — add `.env.test` loading for tests |

### Expected Developer Workflow
```bash
# One-time setup
docker compose up -d db_test

# Run tests (auto-applies migrations to test DB)
cd backend && python -m pytest tests/ -v

# Or with a helper script (to be added in next checkpoint)
./run_tests.sh
```

### Expected CI Workflow
```yaml
# .github/workflows/test.yml (example)
services:
  db_test:
    image: postgres:16-alpine
    env:
      POSTGRES_DB: itms_test
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_pass
    ports: ["5432:5432"]
    options: >-
      --health-cmd "pg_isready -U test_user"
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5

steps:
  - uses: actions/checkout@v4
  - name: Run backend tests
    working-directory: backend
    env:
      DATABASE_URL: postgresql://test_user:test_pass@localhost:5432/itms_test
      SECRET_KEY: test_secret_key_for_ci_only
    run: |
      alembic upgrade head
      python -m pytest tests/ -v
```

---

## D. IMPLEMENTATION PLAN (Next Checkpoint)

1. **Add `db_test` service to `docker-compose.yml`**
   - PostgreSQL 16-alpine, separate volume `postgres_test_data`
   - No port mapping needed (internal network only)
   - Healthcheck for readiness

2. **Create `backend/.env.test`**
   - `DATABASE_URL=postgresql://test_user:test_pass@db_test:5432/itms_test`
   - `SECRET_KEY=test_secret_key_not_for_production`
   - `ENVIRONMENT=test`, `DEBUG=true`
   - Disable rate limiting, SLA monitor, cookie secure, HSTS for test speed

3. **Rewrite `backend/tests/conftest.py`**
   - Remove SQLite engine, `StaticPool`, global session variable
   - Create session-scoped fixture `test_db_engine` pointing to test PostgreSQL
   - Create session-scoped fixture `alembic_migrated_db` that runs `alembic upgrade head` once per session
   - Create function-scoped fixture `db_session` using **transaction rollback** (savepoint/rollback) for isolation — faster than drop/create
   - Keep existing user/auth fixtures (they work with any DB)

4. **Update `backend/pytest.ini`**
   - Add `env_file = .env.test` (requires `pytest-env` plugin) or load in conftest

5. **Add `pytest-env` to `requirements.txt`** (optional but clean)

6. **Verify full test suite passes against PostgreSQL**
   - Run `alembic upgrade head` on test DB
   - Run `pytest tests/` — target: 103 passed
   - Confirm enum, JSON, FK, timestamp, index behavior matches production

7. **Document developer/CI commands in README** (or `TESTING.md`)

---

## SUMMARY

| Item | Status |
|------|--------|
| **Actual backend test count/result** | **103 tests, 103 passed** (3:08) |
| **Current test database** | **SQLite in-memory** (`sqlite:///:memory:`) |
| **Recommended PostgreSQL test approach** | **Dedicated `db_test` service in Docker Compose** (Option A) |
| **Files to modify in NEXT checkpoint** | `docker-compose.yml`, `backend/.env.test` (new), `backend/tests/conftest.py`, `backend/pytest.ini`, `backend/requirements.txt` (add `pytest-env`) |
| **Blockers discovered** | **None** — infrastructure ready, migrations validated, Docker stack healthy |

---

**This checkpoint is complete.** The audit is delivered and the existing test suite has been verified (103/103 passing). The next checkpoint will implement the PostgreSQL test migration per the plan above.
# Production Deployment Guide

This document describes how to deploy the ITMS (Intelligent Ticket Management System) in a production environment.

## Prerequisites

- Docker Engine 24+ and Docker Compose v2+
- A PostgreSQL 16+ database (can be managed externally or via Docker)
- A reverse proxy (nginx, Traefik, Caddy) for HTTPS termination
- Domain name with valid TLS certificate (Let's Encrypt or similar)

## Architecture Overview

```
Internet → Reverse Proxy (HTTPS) → Frontend (nginx) → Backend (FastAPI) → PostgreSQL
                                      ↑
                              Static Assets / SPA
```

### Service Components

| Service | Technology | Port (internal) | Purpose |
|---------|------------|-----------------|---------|
| Frontend | React + Vite + nginx | 80 | Serves SPA, proxies API to backend |
| Backend | FastAPI + Uvicorn | 8000 | REST API, WebSocket, background jobs |
| Database | PostgreSQL 16 + pgvector | 5432 | Primary data store |

## Required Environment Variables

Create a `.env` file in the repository root (or `backend/.env` for backend-only) with the following variables:

### Database

```bash
# Required: PostgreSQL connection string
# Format: postgresql://USER:PASSWORD@HOST:PORT/DATABASE
DATABASE_URL=postgresql://itms_user:CHANGE_ME@db:5432/itms

# For external database (not Docker-managed):
# DATABASE_URL=postgresql://user:pass@external-host:5432/itms
```

### JWT Authentication

```bash
# Required: Generate with: openssl rand -base64 32
SECRET_KEY=your-256-bit-base64-encoded-secret-key

ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### CORS Origins

```bash
# Required: Comma-separated JSON array of allowed origins
# Must include your production frontend URL
CORS_ORIGINS='["https://your-domain.com", "https://www.your-domain.com"]'
```

### File Uploads

```bash
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE_MB=10
```

### Environment

```bash
ENVIRONMENT=production
DEBUG=false
```

### Security Headers & Cookies (Production Defaults)

```bash
# Secure cookies (HTTPS only) - MUST be true in production
COOKIE_SECURE=true
COOKIE_SAMESITE=lax
COOKIE_DOMAIN=your-domain.com  # Optional: set for subdomain sharing

# HSTS - Enable only when serving over HTTPS with valid cert
HSTS_ENABLED=true
HSTS_MAX_AGE=31536000
HSTS_INCLUDE_SUBDOMAINS=true
HSTS_PRELOAD=false

# CSP - Enabled by default
SECURITY_HEADERS_ENABLED=true
CSP_ENABLED=true
```

### Rate Limiting

```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60
AUTH_RATE_LIMIT_REQUESTS=10
AUTH_RATE_LIMIT_WINDOW_SECONDS=300
```

### SLA Monitoring

```bash
SLA_MONITOR_ENABLED=true
SLA_CHECK_INTERVAL_SECONDS=60
```

### Email (SMTP for Production)

```bash
EMAIL_PROVIDER=smtp
EMAIL_FROM_ADDRESS=noreply@your-domain.com
EMAIL_FROM_NAME=ITMS Notifications
SMTP_HOST=smtp.your-provider.com
SMTP_PORT=587
SMTP_USERNAME=your-smtp-user
SMTP_PASSWORD=your-smtp-password
SMTP_USE_TLS=true
SMTP_USE_SSL=false
SMTP_TIMEOUT_SECONDS=10
```

### AI / LLM (Optional)

```bash
AI_PROVIDER=gemini  # or ollama
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-1.5-flash
OLLAMA_MODEL=llama3.2
AI_TEMPERATURE=0.0
AI_MAX_OUTPUT_TOKENS=4096
AI_TIMEOUT_SECONDS=30
```

## Secret Generation

### JWT Secret Key

```bash
# Generate a secure 256-bit key
openssl rand -base64 32
```

### Database Password

```bash
# Generate a secure password
openssl rand -base64 24 | tr -d "=+/" | cut -c1-32
```

### SMTP Password

Use your email provider's app-specific password or SMTP credentials.

## Local Production-Like Startup

For testing production configuration locally without a full reverse proxy:

```bash
# 1. Create production .env file
cp backend/.env.example backend/.env.prod
# Edit backend/.env.prod with production values

# 2. Start with docker-compose using production profile
docker compose --env-file backend/.env.prod up -d --build

# 3. Verify health
curl http://localhost/health        # Frontend
curl http://localhost:8000/health   # Backend liveness
curl http://localhost:8000/ready    # Backend readiness
```

## Docker-Based Deployment

### 1. Prepare Environment

```bash
# Create production environment file
cat > .env.prod <<'EOF'
POSTGRES_DB=itms
POSTGRES_USER=itms_user
POSTGRES_PASSWORD=CHANGE_ME_TO_SECURE_PASSWORD
SECRET_KEY=CHANGE_ME_TO_SECURE_RANDOM_KEY
CORS_ORIGINS='["https://your-domain.com"]'
ENVIRONMENT=production
DEBUG=false
COOKIE_SECURE=true
HSTS_ENABLED=true
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.your-provider.com
SMTP_PORT=587
SMTP_USERNAME=your-smtp-user
SMTP_PASSWORD=your-smtp-password
EOF

# Secure the file
chmod 600 .env.prod
```

### 2. Start the Stack

```bash
# Start all services
docker compose --env-file .env.prod up -d --build

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### 3. Run Migrations (One-off)

For production deployments with multiple replicas, run migrations as a separate step before starting application containers:

```bash
# Run migrations once
docker compose --env-file .env.prod run --rm backend migrate

# Then start application services
docker compose --env-file .env.prod up -d backend frontend
```

### 4. Configure Reverse Proxy

Example nginx configuration for HTTPS termination:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security headers (in addition to application headers)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Frontend
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health checks (optional: restrict to internal)
    location /health {
        proxy_pass http://localhost:8000/health;
    }
    location /ready {
        proxy_pass http://localhost:8000/ready;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

**Important**: When using a reverse proxy, ensure the backend receives the `X-Forwarded-Proto` header so HSTS and secure cookie logic work correctly. The backend checks this header in `SecurityHeadersMiddleware._should_add_hsts()`.

### 5. File Storage Persistence

Uploaded attachments are stored in the `uploads` Docker volume. For production:

- **Backup**: Include the `uploads` volume in your backup strategy
- **External Storage**: For multi-replica deployments, configure `UPLOAD_DIR` to point to a shared network filesystem (NFS, EFS) or object storage (S3-compatible) via application code changes
- **Permissions**: The container runs as non-root user `appuser` (UID 999), ensure the volume is writable by this user

## Database Setup and Migrations

### Initial Setup

```bash
# Start database only
docker compose --env-file .env.prod up -d db

# Wait for health check
docker compose ps

# Run migrations
docker compose --env-file .env.prod run --rm backend migrate
```

### Migration Procedure

```bash
# 1. Backup database (see Backup section)
# 2. Run migrations
docker compose --env-file .env.prod run --rm backend migrate
# 3. Verify
docker compose --env-file .env.prod run --rm backend alembic current
```

### Verifying Migration Status

```bash
# Check current revision
docker compose --env-file .env.prod run --rm backend alembic current

# Show history
docker compose --env-file .env.prod run --rm backend alembic history --verbose
```

## Health Check Verification

### Liveness (`/health`)
- **Purpose**: Confirms the application process is running
- **Expected**: HTTP 200 with `{"status": "healthy", "service": "itms-backend"}`
- **No external dependencies checked**

### Readiness (`/ready`)
- **Purpose**: Confirms the service can handle requests
- **Checks**: Database connectivity, SLA scheduler status
- **Success**: HTTP 200 with `{"status": "ready", ...}`
- **Failure**: HTTP 503 with `{"status": "not ready", ...}`

### Monitoring Integration

```bash
# Kubernetes-style probes
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 20
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30
  failureThreshold: 3
```

## Logging and Troubleshooting

### Structured Logging

The application emits JSON-structured logs to stdout. Key fields:
- `timestamp`: ISO 8601 timestamp
- `level`: Log level (INFO, WARNING, ERROR)
- `logger`: Logger name
- `module`, `function`, `line`: Source location
- `request_id`: Correlation ID from `X-Request-ID` header

### Viewing Logs

```bash
# All services
docker compose logs -f

# Backend only
docker compose logs -f backend

# Filter by request ID
docker compose logs backend | grep "request_id_value"
```

### Common Issues

| Issue | Diagnosis | Resolution |
|-------|-----------|------------|
| Backend fails to start | `docker compose logs backend` | Check DATABASE_URL, SECRET_KEY, migrations |
| Database connection refused | `docker compose logs db` | Verify credentials, network, health check |
| CORS errors | Browser console | Verify CORS_ORIGINS matches frontend origin exactly |
| HTTPS cookie not set | Browser dev tools | Ensure COOKIE_SECURE=true and reverse proxy sets X-Forwarded-Proto |
| Uploads failing | Backend logs | Check UPLOAD_DIR permissions, MAX_UPLOAD_SIZE_MB |

## Backup and Recovery

### Database Backup

```bash
# Create backup
docker compose exec -T db pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > backup_$(date +%F).sql

# Compressed
docker compose exec -T db pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} | gzip > backup_$(date +%F).sql.gz
```

### Volume Backup (Uploads)

```bash
# Backup uploads volume
docker run --rm -v itms_uploads:/data -v $(pwd):/backup alpine tar czf /backup/uploads_$(date +%F).tar.gz -C /data .
```

### Recovery

```bash
# 1. Stop services
docker compose down

# 2. Restore database
docker compose up -d db
# Wait for healthy
cat backup_2026-01-15.sql | docker compose exec -T db psql -U ${POSTGRES_USER} ${POSTGRES_DB}

# 3. Restore uploads
docker run --rm -v itms_uploads:/data -v $(pwd):/backup alpine tar xzf /backup/uploads_2026-01-15.tar.gz -C /data

# 4. Run migrations (if schema changed)
docker compose run --rm backend migrate

# 5. Start all services
docker compose up -d
```

## Safe Upgrade and Rollback Procedures

### Blue-Green Deployment (Recommended)

1. Deploy new version to separate environment
2. Run migrations against new database copy
3. Verify health checks
4. Switch reverse proxy traffic
5. Keep old environment for rollback window

### Rolling Update (Single Environment)

```bash
# 1. Pull/build new images
docker compose --env-file .env.prod build --pull

# 2. Run migrations (one-off)
docker compose --env-file .env.prod run --rm backend migrate

# 3. Rolling restart (if multiple replicas)
# docker compose up -d --no-deps --scale backend=2 backend
# Then scale down old

# 4. Verify
curl https://your-domain.com/health
curl https://your-domain.com/ready
```

### Rollback

```bash
# 1. Revert to previous image tag
# 2. If migration was run, restore database from backup
# 3. Restart services
docker compose up -d
```

## Production Security Checklist

- [ ] `SECRET_KEY` is a strong, randomly generated 256-bit key
- [ ] `DEBUG=false`
- [ ] `COOKIE_SECURE=true`
- [ ] `HSTS_ENABLED=true` (with valid TLS certificate)
- [ ] `CORS_ORIGINS` contains only production frontend URLs
- [ ] Database password is strong and stored securely
- [ ] SMTP credentials use app-specific passwords
- [ ] Reverse proxy terminates TLS with modern configuration
- [ ] Database port (5432) NOT exposed to internet
- [ ] Uploads volume backed up regularly
- [ ] Log aggregation configured (ELK, Loki, Datadog, etc.)
- [ ] Health checks monitored with alerting
- [ ] Rate limiting enabled and tuned
- [ ] Dependency vulnerability scanning in CI (`pip-audit`, `npm audit`)

## Checks Not Run in This Guide

| Check | Status | Reason |
|-------|--------|--------|
| Fresh-database migration test | ✅ PASSED (Milestone 6) | Verified against isolated test DB in CI |
| Load/performance tests | NOT RUN | Not configured in repo; recommend k6 or Locust |
| E2E browser tests | NOT RUN | No Playwright/Cypress configured |
| Docker image vulnerability scan | NOT RUN | Run `docker scout` or `trivy` in CI |
| External PostgreSQL (RDS, Cloud SQL) | NEEDS MANUAL VERIFICATION | Configuration-specific; adjust DATABASE_URL |

## Staging Deployment Rehearsal

For a complete staging deployment checklist with executable verification steps, see:
**[`docs/MILESTONE_7_STAGING_CHECKLIST.md`](MILESTONE_7_STAGING_CHECKLIST.md)**

This checklist covers:
- Safe staging database provisioning
- Migration procedure and verification
- Docker Compose configuration validation
- Application startup and health/readiness checks
- Authentication and role-permission checks
- Ticket creation, assignment, pending, resolution, reopening, closing and escalation checks
- Comments, notifications, attachments and settings checks
- Persistent storage verification
- Backup and restore test
- Failure-recovery and troubleshooting steps
- Rollback considerations, including database compatibility
- Security checks before admitting real users
- Explicit acceptance criteria and a final go/no-go decision

## Environment-Specific Configuration

### Kubernetes

See `docs/kubernetes/` (if available) for Helm charts or Kustomize overlays. Key adjustments:
- Use `Deployment` with `readinessProbe`/`livenessProbe` pointing to `/ready`/`/health`
- Use `Secret` for `SECRET_KEY`, database password, SMTP password
- Use `PersistentVolumeClaim` for `uploads` volume
- Configure `HorizontalPodAutoscaler` based on CPU/memory

### Cloud SQL / RDS / Managed PostgreSQL

- Set `DATABASE_URL` to managed instance endpoint
- Ensure `sslmode=require` in connection string
- Remove `db` service from docker-compose
- Run migrations from CI/CD pipeline or init container

### Docker Swarm / Nomad

- Use `deploy:` section in docker-compose for replicas, constraints, resources
- Use configs/secrets for environment variables
- Health checks map to Swarm health checks automatically

## Appendix: Default Ports

| Service | Container Port | Host Port (dev) | Production |
|---------|---------------|-----------------|------------|
| Frontend (nginx) | 80 | 80 | Behind reverse proxy |
| Backend (FastAPI) | 8000 | 8000 | Behind reverse proxy |
| PostgreSQL | 5432 | 5434 (dev only) | Internal only |
| PostgreSQL Test | 5432 | 5433 | Test profile only |

## Support

For deployment issues:
1. Check `docker compose logs -f <service>`
2. Verify health endpoints
3. Review this guide's troubleshooting section
4. Check application logs for request IDs
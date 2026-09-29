# Docker Deployment

## Prerequisites

- Docker Engine
- Docker Compose

## Starting the stack

```bash
docker compose up -d
```

## Stopping the stack

```bash
docker compose down
```

## Viewing logs

```bash
docker compose logs -f
```

To view logs for a specific service:

```bash
docker compose logs -f backend
```

## Running migrations

Migrations are not run automatically on startup. To apply migrations to the database, run:

```bash
docker compose exec backend alembic upgrade head
```

## Rebuilding containers

```bash
docker compose build
```

## Accessing frontend/backend

- Frontend: http://localhost
- Backend API: http://localhost:8000
- API documentation: http://localhost:8000/docs

## PostgreSQL connection details for development

If you need to connect to the PostgreSQL database from your host machine (for example, using a GUI tool), use:

- Host: localhost
- Port: 5432 (or the port you mapped)
- Database: itms (or as set in POSTGRES_DB)
- User: itms_user (or as set in POSTGRES_USER)
- Password: itms_pass (or as set in POSTGRES_PASSWORD)

Note: In the docker-compose.yml, we expose the PostgreSQL port only to other containers by default (not to the host). To connect from the host, you need to add a port mapping, e.g., "5432:5432" under the db service. For development, you can uncomment the ports line.

## Troubleshooting common startup problems

### Database connection failures

Ensure that the database service is healthy. Check the logs:

```bash
docker compose logs db
```

If the backend cannot connect to the database, verify that the DATABASE_URL in the backend environment is correct. In the compose file, we set it to use the db service hostname.

### Backend fails to start

Check the backend logs:

```bash
docker compose logs backend
```

### Frontend not serving

Check the frontend logs and ensure the build step succeeded.

### Missing uploads directory

The uploads directory is persisted via a named volume. If you lose uploads, check the volume.

## Notes

- The backend uses the PostgreSQL service hostname `db` when running in Compose.
- The `/ready` endpoint checks database connectivity.
- File uploads are stored in the `uploads` directory, which is mounted as a Docker volume.

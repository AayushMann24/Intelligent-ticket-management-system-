#!/bin/sh
# Backend entrypoint script
# Supports running migrations separately from application startup.
# Usage:
#   /app/entrypoint.sh migrate    - Run migrations only (for one-off migration jobs)
#   /app/entrypoint.sh start      - Run migrations then start application (default)
#   /app/entrypoint.sh            - Same as 'start'

set -e

COMMAND="${1:-start}"

case "$COMMAND" in
    migrate)
        echo "Running database migrations..."
        alembic upgrade head
        echo "Migrations completed."
        ;;
    start)
        echo "Running database migrations..."
        alembic upgrade head
        echo "Migrations completed. Starting application..."
        exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
        ;;
    *)
        echo "Unknown command: $COMMAND"
        echo "Usage: $0 [migrate|start]"
        exit 1
        ;;
esac
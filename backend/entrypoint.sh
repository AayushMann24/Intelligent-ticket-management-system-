#!/bin/sh
# Backend entrypoint script
# Runs Alembic migrations before starting the application

set -e

echo "Running database migrations..."
alembic upgrade head

echo "Migrations completed. Starting application..."
exec "$@"
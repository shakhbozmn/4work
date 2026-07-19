#!/bin/bash
set -euo pipefail

DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}

echo "=================================="
echo "Starting entrypoint script..."
echo "=================================="

echo "Waiting for PostgreSQL..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done
echo "PostgreSQL is ready!"

echo "Fixing volume permissions..."
chown -R appuser:appuser /app/staticfiles /app/media

echo "Running migrations..."
gosu appuser python manage.py migrate --noinput

echo "Collecting static files..."
gosu appuser python manage.py collectstatic --noinput --clear

echo "=================================="
echo "Starting Gunicorn as appuser..."
echo "=================================="

echo "=== Gunicorn Diagnostic Info ==="
echo "Gunicorn version:"
gunicorn --version
echo "Running as user: $(gosu appuser whoami)"
echo "=== End Diagnostic Info ==="

exec gosu appuser gunicorn --config config/gunicorn.py config.wsgi:application

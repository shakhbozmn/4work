#!/bin/bash
set -euo pipefail

if [ -f .env.production ]; then
    set -a
    source .env.production
    set +a
fi

if [[ -z "${DOCKER_IMAGE:-}" ]]; then
    echo "ERROR: DOCKER_IMAGE environment variable is not set."
    exit 1
fi

echo "========================================="
echo "Starting Deployment Process"
echo "========================================="

echo "Pulling latest code from git..."
git pull origin main

echo "Fetching latest Docker image..."
docker compose pull web

echo "Ensuring db, redis, and nginx are running..."
docker compose up -d db redis nginx

echo "Redeploying web service..."
docker compose up -d --no-deps --force-recreate web

echo "Running database migrations..."
docker compose exec -T web python manage.py migrate --noinput

echo "Collecting static files..."
docker compose exec -T web python manage.py collectstatic --noinput

echo "Waiting for web container to become healthy..."
ATTEMPTS=0
MAX_ATTEMPTS=30
until [ "$ATTEMPTS" -ge "$MAX_ATTEMPTS" ]; do
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' 4work_app 2>/dev/null || echo "missing")
    if [ "$STATUS" = "healthy" ]; then
        echo "Web container reports healthy."
        break
    fi
    ATTEMPTS=$((ATTEMPTS + 1))
    echo "  attempt $ATTEMPTS/$MAX_ATTEMPTS — status: $STATUS"
    sleep 2
done

if [ "$ATTEMPTS" -ge "$MAX_ATTEMPTS" ]; then
    echo "ERROR: web container did not become healthy in time."
    docker logs --tail 100 4work_app
    exit 1
fi

echo "========================================="
echo "Container Status:"
docker compose ps

echo "========================================="
echo "Recent logs from app container:"
docker logs --tail 50 4work_app

echo "========================================="
echo "Deployment completed!"
echo "========================================="

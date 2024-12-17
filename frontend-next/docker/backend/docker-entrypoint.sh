#!/bin/bash

# Exit on error
set -e

# Function to wait for a service
wait_for() {
    local host="$1"
    local port="$2"
    local service="$3"
    local retries=5
    local wait=1

    echo "Waiting for $service to be ready..."
    for i in $(seq 1 $retries); do
        nc -z "$host" "$port" && echo "$service is ready!" && return
        echo "$service is not ready. Retrying in ${wait}s..."
        sleep $wait
        wait=$((wait * 2))
    done
    echo "$service is not available" && exit 1
}

# Wait for required services
if [ "$DATABASE_HOST" ]; then
    wait_for "$DATABASE_HOST" "${DATABASE_PORT:-5432}" "PostgreSQL"
fi

if [ "$REDIS_HOST" ]; then
    wait_for "$REDIS_HOST" "${REDIS_PORT:-6379}" "Redis"
fi

# Apply database migrations
echo "Applying database migrations..."
alembic upgrade head

# Start the application
echo "Starting application..."
exec "$@"

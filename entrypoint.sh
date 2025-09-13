#!/bin/sh

# Exit immediately if a command exits with a non-zero status ('e')
# or if an unset variable is used ('u').
set -eu

# Wait for the database to be ready
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}
WAIT_TIMEOUT=${WAIT_TIMEOUT:-60}

echo "Waiting for database connection at ${DB_HOST}:${DB_PORT}..."

count=0
while ! python -c "import socket; socket.create_connection(('${DB_HOST}', ${DB_PORT}), timeout=1).close()" 2>/dev/null; do
    count=$((count + 1))
    if [ ${count} -ge ${WAIT_TIMEOUT} ]; then
        echo "Error: Timed out waiting for database connection at ${DB_HOST}:${DB_PORT}" >&2
        exit 1
    fi
    echo "Waiting for database connection... (${count}/${WAIT_TIMEOUT}s)"
    sleep 1
done

echo "Database is ready."

# Apply database migrations
echo "Applying database migrations..."
if [ -f /app/.venv/bin/python ]; then
    /app/.venv/bin/python manage.py migrate --noinput
else
    echo "Using PATH python (venv not found at expected location)"
    python manage.py migrate --noinput
fi

# Start the API server with Gunicorn
echo "Starting API server..."
# System Python has gunicorn installed via Dockerfile, so use it directly
echo "Using system gunicorn (installed via Dockerfile)"
PORT="${PORT:-8000}"
WORKERS="${GUNICORN_WORKERS:-2}"
THREADS="${GUNICORN_THREADS:-4}"
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:"${PORT}" \
  --workers "${WORKERS}" \
  --threads "${THREADS}" \
  --access-logfile - \
  --error-logfile -

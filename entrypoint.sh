#!/bin/bash
set -e

echo "=== Running database migrations ==="
flask db upgrade

echo "=== Starting Gunicorn ==="
exec gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 4 --timeout 30 app:app

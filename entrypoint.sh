#!/bin/bash
set -e

echo "=== Running database migrations ==="
flask db upgrade

echo "=== Starting Gunicorn ==="
exec gunicorn -c gunicorn.conf.py app:app

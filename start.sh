#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -f ".env" ]]; then
  echo "Missing .env. Copy .env.example to .env and update values first."
  exit 1
fi

python -m pip install -r requirements.txt

export FLASK_APP=manage.py
flask db upgrade

# Seed only on first run; endpoint safely skips if data already exists.
python -c "from e16_app import create_app; app=create_app(); c=app.test_client(); r=c.get('/seed'); print(r.status_code, r.data.decode())"

echo "E16 is running at http://127.0.0.1:5000"
python app.py

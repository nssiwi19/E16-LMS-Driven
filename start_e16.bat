@echo off
cd /d "%~dp0"

if not exist ".env" (
    echo [ERROR] Missing .env. Copy .env.example to .env and update values first.
    exit /b 1
)

python -m pip install -r requirements.txt

set FLASK_APP=app.py
flask db upgrade
flask seed

echo [SUCCESS] E16 is running at http://127.0.0.1:5000
python app.py

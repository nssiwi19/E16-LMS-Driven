# E16 LMS (Data-Driven MVP)

Flask-based LMS MVP for E16 MCNA with a data-first design:
- Auth + role routing (`student`, `teacher`, `admin`)
- Course/Lesson management
- Learning flow with event logs (`start`, `complete`)
- Analytics dashboard + CSV export for DA workflow

## Tech Stack
- Python 3.12+
- Flask, Flask-SQLAlchemy, Flask-Migrate
- Flask-Login
- SQLite (dev default), configurable via `DATABASE_URL`
- Chart.js (CDN in template) for dashboard chart

## Quick Start (Windows CMD)
```bat
cd /d "c:\path\to\E16"
copy .env.example .env
notepad .env
python -m pip install -r requirements.txt
set FLASK_APP=manage.py
flask db upgrade
python -c "from e16_app import create_app; app=create_app(); c=app.test_client(); print(c.get('/seed').status_code)"
python app.py
```

Open: `http://127.0.0.1:5000`

## Quick Start Scripts
- Windows PowerShell: `.\start_e16.ps1`
- Linux/macOS: `bash ./start.sh`

Both scripts:
- install dependencies
- run migrations
- call `/seed` (safe if data already exists)
- run server

## Environment Variables
Copy `.env.example` to `.env` and set values.

Required:
- `SECRET_KEY`
- `E16_SEED_PASSWORD` (required for `/seed` and `verify.py`)

Common:
- `DATABASE_URL` (default: `sqlite:///e16.db`)
- `FLASK_DEBUG` (`true` or `false`)
- `PORT` (default `5000`)
- `E16_SEED_STUDENT_EMAIL`, `E16_SEED_TEACHER_EMAIL`, `E16_SEED_ADMIN_EMAIL`

## Verify PRD/DA Focus
Run:
```bash
python verify.py
```

`verify.py` asserts:
- login works and updates `login_count`, `last_login`
- `start` log is created when entering learning page
- `complete` log is created on "Mark as Complete"
- analytics page responds and contains chart script (`new Chart(...)`)
- CSV export includes required columns:
  `student_email, course_title, lesson_title, action_type, timestamp`

## Project Structure
```
e16_app/
  blueprints/
    auth.py
    teacher.py
    student.py
    analytics.py
  models.py
  services.py
  extensions.py
migrations/
templates/
static/
```

## Security Notes
- No default seed password is hardcoded in source.
- Use `.env` for secrets and seed credentials.
- `.env` and local DB files are ignored by git.

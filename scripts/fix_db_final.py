import os
from dotenv import load_dotenv
from e16_app import create_app
from e16_app.extensions import db

load_dotenv()
db_url = os.getenv("DATABASE_URL", "sqlite:///e16.db")
db_path = db_url.replace("sqlite:///", "")

print(f"Targeting DB: {db_path}")

# 1. Kill old DB
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print("Removed existing DB file.")
    except Exception as e:
        print(f"Could not remove DB (maybe in use?): {e}")

# 2. Create App & Tables
app = create_app()
with app.app_context():
    print("Creating all tables...")
    # Temporarily re-enable create_all
    db.create_all()
    print("Tables created successfully.")
    
    # 3. Stamp with Alembic (Bypass migrate/upgrade)
    try:
        from flask_migrate import stamp
        print("Stamping database as 'head'...")
        stamp()
        print("Database is now synced with Migrations!")
    except Exception as e:
        print(f"Stamping failed (not critical if tables exist): {e}")

print("\n--- DONE! You can now run 'python app.py' ---")

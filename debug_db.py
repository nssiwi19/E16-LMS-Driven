import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL", "sqlite:///e16.db")
print(f"DATABASE_URL from .env: {db_url}")

db_path = db_url.replace("sqlite:///", "")
print(f"Checking file: {os.path.abspath(db_path)}")

if os.path.exists(db_path):
    print(f"File size: {os.path.getsize(db_path)} bytes")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables in DB: {[t[0] for t in tables]}")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version';")
        if cursor.fetchone():
            cursor.execute("SELECT version_num FROM alembic_version")
            print(f"Alembic Version: {cursor.fetchone()}")
        else:
            print("Table 'alembic_version' NOT FOUND.")
        conn.close()
    except Exception as e:
        print(f"Error accessing DB: {e}")
else:
    print("Database file NOT FOUND.")

print(f"\nMigrations folder exists: {os.path.exists('migrations')}")
if os.path.exists("migrations/versions"):
    print(f"Versions found: {os.listdir('migrations/versions')}")

# -*- coding: utf-8 -*-
import os
import sys
import time
import tarfile
import sqlite3
import subprocess
from datetime import datetime, timedelta
from urllib.parse import urlparse
from dotenv import load_dotenv

# Ensure E16 project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

# Load environment variables
load_dotenv()

BACKUP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "backups"))
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///instance/e16.db")

def ensure_backup_dir():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"Created backup directory: {BACKUP_DIR}")

def backup_sqlite(db_path):
    print("Initiating SQLite online database backup...")
    
    # Resolve relative database path
    clean_path = db_path.replace("sqlite:///", "")
    if not os.path.isabs(clean_path):
        root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, clean_path))
        instance_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "instance", clean_path))
        
        if os.path.exists(root_path):
            clean_path = root_path
        elif os.path.exists(instance_path):
            clean_path = instance_path
        else:
            # Try instance folder directly as fallback
            clean_path = instance_path
        
    if not os.path.exists(clean_path):
        print(f"Error: SQLite source database not found at {clean_path}")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_backup = os.path.join(BACKUP_DIR, f"temp_backup_{timestamp}.db")
    archive_name = os.path.join(BACKUP_DIR, f"db_backup_{timestamp}.tar.gz")

    try:
        # Perform safe online backup using sqlite3 backup API (non-blocking)
        src = sqlite3.connect(clean_path)
        dst = sqlite3.connect(temp_backup)
        with dst:
            src.backup(dst)
        dst.close()
        src.close()
        
        # Compress SQLite backup file
        with tarfile.open(archive_name, "w:gz") as tar:
            tar.add(temp_backup, arcname=os.path.basename(clean_path))
            
        # Clean up temp file
        os.remove(temp_backup)
        print(f"SQLite online backup completed successfully: {archive_name}")
        return archive_name
    except Exception as e:
        print(f"SQLite backup failed: {str(e)}")
        if os.path.exists(temp_backup):
            os.remove(temp_backup)
        return None

def backup_postgres(db_url):
    print("Initiating PostgreSQL database backup...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = os.path.join(BACKUP_DIR, f"db_backup_{timestamp}.sql.tar.gz")
    temp_sql = os.path.join(BACKUP_DIR, f"temp_backup_{timestamp}.sql")
    
    try:
        # Parse connection URI
        result = urlparse(db_url)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = result.port or 5432
        
        # Setup environment containing pg password to prevent prompt
        env = os.environ.copy()
        if password:
            env["PGPASSWORD"] = password
            
        cmd = [
            "pg_dump",
            "-h", hostname,
            "-p", str(port),
            "-U", username,
            "-F", "p",  # Plain text SQL format
            "-f", temp_sql,
            database
        ]
        
        print(f"Executing pg_dump for database '{database}' on host '{hostname}'...")
        res = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True)
        
        # Compress the SQL dump
        with tarfile.open(archive_name, "w:gz") as tar:
            tar.add(temp_sql, arcname=f"{database}_backup_{timestamp}.sql")
            
        # Clean up temp file
        os.remove(temp_sql)
        print(f"PostgreSQL backup completed successfully: {archive_name}")
        return archive_name
    except subprocess.CalledProcessError as e:
        print(f"PostgreSQL backup via pg_dump failed: {e.stderr}")
        if os.path.exists(temp_sql):
            os.remove(temp_sql)
        return None
    except Exception as e:
        print(f"PostgreSQL backup failed: {str(e)}")
        if os.path.exists(temp_sql):
            os.remove(temp_sql)
        return None

def clean_old_backups(days=7):
    print(f"Cleaning up backups older than {days} days...")
    now = time.time()
    cutoff = now - (days * 86400)
    
    for filename in os.listdir(BACKUP_DIR):
        if not filename.startswith("db_backup_") or not filename.endswith(".tar.gz"):
            continue
            
        filepath = os.path.join(BACKUP_DIR, filename)
        file_creation_time = os.path.getmtime(filepath)
        
        if file_creation_time < cutoff:
            try:
                os.remove(filepath)
                print(f"Deleted outdated backup file: {filename}")
            except Exception as e:
                print(f"Failed to delete outdated backup {filename}: {str(e)}")

def run_backup():
    ensure_backup_dir()
    
    print(f"Backup script started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target Database URL: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
    
    backup_file = None
    if DATABASE_URL.startswith("sqlite"):
        backup_file = backup_sqlite(DATABASE_URL)
    elif DATABASE_URL.startswith("postgresql") or DATABASE_URL.startswith("postgres"):
        backup_file = backup_postgres(DATABASE_URL)
    else:
        print(f"Unsupported database URL schema: {DATABASE_URL}")
        
    if backup_file:
        clean_old_backups(days=7)
        print("Backup process finished successfully!")
        return 0
    else:
        print("Backup process failed!")
        return 1

if __name__ == "__main__":
    sys.exit(run_backup())

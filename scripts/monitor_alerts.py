# -*- coding: utf-8 -*-
import os
import sys
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
PORT = os.environ.get("PORT", "5000")
TARGET_HOST = os.environ.get("MONITOR_TARGET_HOST", f"http://127.0.0.1:{PORT}")
METRICS_TOKEN = os.environ.get("METRICS_TOKEN", "")

INSTANCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "instance"))
ALERTS_LOG = os.path.join(INSTANCE_DIR, "alerts.log")

def log_alert(level, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alert_line = f"[{timestamp}] [{level.upper()}] {message}\n"
    
    # Ensure instance directory exists
    if not os.path.exists(INSTANCE_DIR):
        os.makedirs(INSTANCE_DIR)
        
    with open(ALERTS_LOG, "a", encoding="utf-8") as f:
        f.write(alert_line)
        
    # Print to console with nice coloring
    color_code = "\033[91m" if level.lower() == "critical" else "\033[93m"
    reset_code = "\033[0m"
    print(f"{color_code}{alert_line.strip()}{reset_code}")

def check_liveness():
    url = f"{TARGET_HOST}/healthz"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"Liveness Check (/healthz): OK (HTTP {response.status_code})")
            return True
        else:
            log_alert("warning", f"Liveness check returned unexpected status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        log_alert("critical", f"Liveness check failed. Server is unreachable at {url}. Error: {str(e)}")
        return False

def check_readiness():
    url = f"{TARGET_HOST}/readyz"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("database") == "connected":
                print("Readiness Check (/readyz): OK (Database connected)")
                return True
            else:
                log_alert("critical", f"Readiness check failed. Database is disconnected: {response.text}")
                return False
        else:
            log_alert("critical", f"Readiness check failed with status code {response.status_code}: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        log_alert("critical", f"Readiness check failed. Server is unreachable at {url}. Error: {str(e)}")
        return False

def check_metrics():
    url = f"{TARGET_HOST}/metricsz"
    headers = {}
    if METRICS_TOKEN:
        headers["X-Metrics-Token"] = METRICS_TOKEN
        
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("--- System Metrics Summary ---")
            print(f"Total Users: {data.get('users_total')}")
            print(f"Active Users: {data.get('users_active')}")
            print(f"Published Courses: {data.get('courses_published')}")
            print(f"Total Enrollments: {data.get('enrollments_total')}")
            print(f"Learning Logs Today: {data.get('learning_logs_today')}")
            print(f"Unread Notifications: {data.get('notifications_unread')}")
            
            # Simple threshold checks for potential issues
            unread_notifs = data.get('notifications_unread', 0)
            if unread_notifs > 1000:
                log_alert("warning", f"Extremely high count of unread notifications: {unread_notifs}. Background job workers might be sluggish.")
                
            active_pct = (data.get('users_active', 0) / max(data.get('users_total', 1), 1)) * 100
            if active_pct < 20:
                log_alert("warning", f"Active user ratio is quite low: {active_pct:.1f}% (Total: {data.get('users_total')}, Active: {data.get('users_active')})")
            
            return True
        elif response.status_code == 403:
            print("Metrics Check: Forbidden (Access token required or invalid)")
            return True
        else:
            log_alert("warning", f"Metrics check returned status code {response.status_code}: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        log_alert("warning", f"Metrics check failed. Server is unreachable at {url}. Error: {str(e)}")
        return False

def run_monitoring():
    print(f"=== E16 LMS Self-Monitoring Script ===")
    print(f"Target host: {TARGET_HOST}")
    print(f"Alerts log file: {ALERTS_LOG}")
    print("=======================================")
    
    live = check_liveness()
    ready = check_readiness()
    metrics = check_metrics() if live else False
    
    if not live or not ready:
        print("\nSystem status: OUTAGE / DEGRADED [OUTAGE]")
        return 1
    else:
        print("\nSystem status: HEALTHY [OK]")
        return 0

if __name__ == "__main__":
    sys.exit(run_monitoring())

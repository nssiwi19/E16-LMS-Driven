import json
import time
import threading
from datetime import datetime, timezone
import traceback
from flask import current_app
from ..extensions import db
from ..models import BackgroundJob
from .mail import send_email

_TASK_HANDLERS = {}

def register_task(task_name):
    """
    Decorator to register a background task handler.
    """
    def decorator(func):
        _TASK_HANDLERS[task_name] = func
        return func
    return decorator

# Register standard task handlers
@register_task("send_email")
def handle_send_email(payload):
    """
    Handles sending emails in the background.
    """
    to = payload.get("to")
    subject = payload.get("subject")
    template_name = payload.get("template_name")
    kwargs = payload.get("kwargs", {})
    return send_email(to=to, subject=subject, template_name=template_name, **kwargs)

@register_task("dummy_task")
def handle_dummy_task(payload):
    """
    A simple dummy task for testing background execution.
    """
    current_app.logger.info(f"Dummy task executed successfully with payload: {payload}")
    return True

def enqueue_job(task_name, payload=None):
    """
    Enqueues a new background job into the database.
    """
    if payload is None:
        payload = {}
    
    if task_name not in _TASK_HANDLERS:
        current_app.logger.warning(f"Enqueuing task with unregistered handler: {task_name}")

    payload_str = json.dumps(payload)
    job = BackgroundJob(
        task_name=task_name,
        payload=payload_str,
        status="pending",
        attempts=0,
        max_attempts=3
    )
    db.session.add(job)
    db.session.commit()
    return job.id

def run_pending_jobs(app):
    """
    Finds and runs pending background jobs inside the Flask application context.
    """
    with app.app_context():
        # Select pending jobs, or jobs that are failed but still have attempts remaining
        jobs = db.session.query(BackgroundJob).filter(
            BackgroundJob.status.in_(["pending", "failed"]),
            BackgroundJob.attempts < BackgroundJob.max_attempts
        ).order_by(BackgroundJob.created_at.asc()).all()

        if not jobs:
            return

        for job in jobs:
            job.status = "running"
            job.started_at = datetime.now(timezone.utc)
            job.attempts += 1
            db.session.commit()

            handler = _TASK_HANDLERS.get(job.task_name)
            if not handler:
                job.status = "failed"
                job.error_message = f"No handler registered for task: {job.task_name}"
                job.completed_at = datetime.now(timezone.utc)
                db.session.commit()
                continue

            try:
                payload = json.loads(job.payload)
                result = handler(payload)
                
                if result is False:
                    raise Exception("Task handler returned False (failed).")
                
                job.status = "completed"
                job.error_message = None
            except Exception as e:
                db.session.rollback()
                error_msg = f"{str(e)}\n{traceback.format_exc()}"
                job.error_message = error_msg
                if job.attempts >= job.max_attempts:
                    job.status = "failed"
                else:
                    job.status = "pending"  # Will retry in next run
            finally:
                job.completed_at = datetime.now(timezone.utc)
                db.session.commit()

def start_background_worker(app):
    """
    Starts a daemon thread to process jobs automatically in the background.
    """
    def worker_loop():
        # Give Flask app a few seconds to boot completely
        time.sleep(3)
        with app.app_context():
            app.logger.info("Background job daemon thread initialized successfully.")
            
        while True:
            try:
                run_pending_jobs(app)
            except Exception as e:
                try:
                    with app.app_context():
                        app.logger.error(f"Error in background job daemon thread: {str(e)}")
                except Exception:
                    pass
            time.sleep(5)  # Poll the database every 5 seconds

    thread = threading.Thread(target=worker_loop, daemon=True)
    thread.start()

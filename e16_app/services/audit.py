import json
from flask import request
from flask_login import current_user
from ..extensions import db
from ..models import AuditLog

def log_action(action, target_type=None, target_id=None, detail=None):
    """
    Logs an administrative or significant user action.
    """
    actor_id = current_user.id if current_user.is_authenticated else None
    
    # Try to get IP address
    ip_address = request.remote_addr if request else "Unknown"
    
    # Detail can be a dict, convert to JSON
    detail_str = json.dumps(detail) if detail else None
    
    log = AuditLog(
        actor_id=actor_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail=detail_str,
        ip_address=ip_address
    )
    db.session.add(log)
    db.session.commit()
    return log

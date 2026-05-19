from ..extensions import db
from ..models import Notification
from ..time_utils import utcnow

def notify(user_id, type, message, link=None):
    """
    Creates a new notification for a specific user.
    Types: 'new_assignment', 'graded', 'announcement', 'forum_reply', 'new_quiz'
    """
    notification = Notification(
        user_id=user_id,
        type=type,
        message=message,
        link=link,
        created_at=utcnow()
    )
    db.session.add(notification)
    db.session.commit()
    return notification

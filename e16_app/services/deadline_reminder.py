# -*- coding: utf-8 -*-
"""
Deadline Reminder Service for E16 LMS.
Checks upcoming quiz and assignment deadlines and creates notifications
for enrolled students at 24h and 1h before the deadline.

Usage (CLI):
    flask check-deadlines          # Run once
    # Or schedule via cron / Windows Task Scheduler every 30 minutes
"""
from datetime import timedelta

from ..extensions import db
from ..models import (
    Quiz, Assignment, Enrollment, Notification, Course
)
from ..time_utils import utcnow


def check_and_notify_deadlines():
    """
    Scans all upcoming quiz and assignment deadlines.
    Creates notifications for enrolled students at two thresholds:
      - 24 hours before deadline (type: 'deadline_24h')
      - 1 hour before deadline  (type: 'deadline_1h')

    Idempotent: will not create duplicate notifications for the
    same (user, type, deadline_item) combination.
    """
    now = utcnow()
    created_count = 0

    # --- Quiz deadlines ---
    upcoming_quizzes = db.session.query(Quiz).filter(
        Quiz.due_date != None,
        Quiz.due_date > now,
        Quiz.is_published == True
    ).all()

    for quiz in upcoming_quizzes:
        time_left = quiz.due_date - now
        thresholds = _get_thresholds(time_left)
        if not thresholds:
            continue

        # Find enrolled students for this course
        course = db.session.get(Course, quiz.course_id)
        if not course or course.is_deleted:
            continue

        enrolled_user_ids = [
            e.user_id for e in db.session.query(Enrollment.user_id).filter(
                Enrollment.course_id == quiz.course_id,
                Enrollment.status.in_(["active", "completed"])
            ).all()
        ]

        for uid in enrolled_user_ids:
            for threshold_type, message_prefix in thresholds:
                _create_if_not_exists(
                    uid, threshold_type,
                    f"{message_prefix}: Quiz \"{quiz.title}\" (khóa {course.title}) "
                    f"hết hạn lúc {quiz.due_date.strftime('%d/%m/%Y %H:%M')}.",
                    link=f"/courses/{quiz.course_id}/learn"
                )
                created_count += 1

    # --- Assignment deadlines ---
    upcoming_assignments = db.session.query(Assignment).filter(
        Assignment.deadline != None,
        Assignment.deadline > now
    ).all()

    for assign in upcoming_assignments:
        time_left = assign.deadline - now
        thresholds = _get_thresholds(time_left)
        if not thresholds:
            continue

        course = db.session.get(Course, assign.course_id)
        if not course or course.is_deleted:
            continue

        enrolled_user_ids = [
            e.user_id for e in db.session.query(Enrollment.user_id).filter(
                Enrollment.course_id == assign.course_id,
                Enrollment.status.in_(["active", "completed"])
            ).all()
        ]

        for uid in enrolled_user_ids:
            for threshold_type, message_prefix in thresholds:
                _create_if_not_exists(
                    uid, threshold_type,
                    f"{message_prefix}: Bài tập \"{assign.title}\" (khóa {course.title}) "
                    f"hết hạn lúc {assign.deadline.strftime('%d/%m/%Y %H:%M')}.",
                    link=f"/courses/{assign.course_id}/learn"
                )
                created_count += 1

    db.session.commit()
    return created_count


def _get_thresholds(time_left: timedelta):
    """
    Determine which reminder thresholds apply based on time remaining.
    Returns list of (notification_type, message_prefix) tuples.
    """
    results = []
    total_minutes = time_left.total_seconds() / 60

    # 24h window: between 23h and 25h remaining
    if 23 * 60 <= total_minutes <= 25 * 60:
        results.append(("deadline_24h", "⏰ Còn 24 giờ"))

    # 1h window: between 30min and 90min remaining
    if 30 <= total_minutes <= 90:
        results.append(("deadline_1h", "🔴 Còn 1 giờ"))

    return results


def _create_if_not_exists(user_id, notif_type, message, link=None):
    """
    Only create notification if there isn't already one with the same
    user_id, type, and message (dedup).
    """
    exists = db.session.query(Notification.id).filter(
        Notification.user_id == user_id,
        Notification.type == notif_type,
        Notification.message == message
    ).first()

    if not exists:
        db.session.add(Notification(
            user_id=user_id,
            type=notif_type,
            message=message,
            link=link,
            created_at=utcnow()
        ))

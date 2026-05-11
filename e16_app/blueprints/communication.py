from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify
from flask_login import current_user
from sqlalchemy import func

from ..auth_utils import login_required, role_required
from ..extensions import db
from ..models import Notification, Announcement, ForumThread, ForumReply, Course, Enrollment, User
from ..services.notifications import notify

bp = Blueprint("communication", __name__)

# --- Notifications ---

@bp.route("/notifications")
@login_required
def list_notifications():
    notifications = db.session.query(Notification).filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template("notifications.html", notifications=notifications)

@bp.post("/notifications/<notif_id>/read")
@login_required
def mark_read(notif_id):
    notif = db.session.get(Notification, notif_id)
    if notif and notif.user_id == current_user.id:
        notif.is_read = True
        db.session.commit()
    return redirect(request.referrer or url_for("communication.list_notifications"))

@bp.post("/notifications/read-all")
@login_required
def read_all():
    db.session.query(Notification).filter_by(user_id=current_user.id).update({Notification.is_read: True})
    db.session.commit()
    return redirect(url_for("communication.list_notifications"))

# --- Announcements ---

@bp.route("/courses/<course_id>/announcements")
@login_required
def list_announcements(course_id):
    course = db.session.get(Course, course_id)
    announcements = db.session.query(Announcement).filter_by(course_id=course_id).order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc()).all()
    return render_template("announcements.html", course=course, announcements=announcements)

@bp.post("/teacher/courses/<course_id>/announcements/new")
@login_required
@role_required("teacher")
def create_announcement(course_id):
    course = db.session.get(Course, course_id)
    if not course or course.teacher_id != current_user.id:
        return redirect(url_for("teacher.manage_courses"))
        
    title = request.form.get("title")
    body = request.form.get("body")
    is_pinned = 'is_pinned' in request.form
    
    announcement = Announcement(
        course_id=course_id,
        author_id=current_user.id,
        title=title,
        body=body,
        is_pinned=is_pinned
    )
    db.session.add(announcement)
    db.session.commit()
    
    # Notify all enrolled students
    students = db.session.query(Enrollment).filter_by(course_id=course_id).all()
    for en in students:
        notify(
            user_id=en.user_id,
            type="announcement",
            message=f"Thông báo mới từ giảng viên trong khóa học {course.title}: {title}",
            link=url_for("communication.list_announcements", course_id=course_id)
        )
        
    flash("Đã đăng thông báo mới!", "success")
    return redirect(url_for("communication.list_announcements", course_id=course_id))

# --- Forum ---

@bp.route("/courses/<course_id>/forum")
@login_required
def course_forum(course_id):
    course = db.session.get(Course, course_id)
    # Check enrollment
    is_enrolled = db.session.query(Enrollment).filter_by(user_id=current_user.id, course_id=course_id).first()
    if not is_enrolled and current_user.role != 'admin' and course.teacher_id != current_user.id:
        flash("Bạn cần đăng ký khóa học để tham gia diễn đàn.", "warning")
        return redirect(url_for("student.list_courses"))
        
    threads = db.session.query(ForumThread, User).join(User, User.id == ForumThread.author_id).filter(ForumThread.course_id == course_id).order_by(ForumThread.is_pinned.desc(), ForumThread.created_at.desc()).all()
    return render_template("forum.html", course=course, threads=threads)

@bp.post("/courses/<course_id>/forum/new")
@login_required
def create_thread(course_id):
    title = request.form.get("title")
    body = request.form.get("body")
    
    thread = ForumThread(
        course_id=course_id,
        author_id=current_user.id,
        title=title,
        body=body
    )
    db.session.add(thread)
    db.session.commit()
    flash("Đã đăng chủ đề mới!", "success")
    return redirect(url_for("communication.course_forum", course_id=course_id))

@bp.route("/courses/<course_id>/forum/<thread_id>")
@login_required
def view_thread(course_id, thread_id):
    course = db.session.get(Course, course_id)
    thread = db.session.query(ForumThread, User).join(User, User.id == ForumThread.author_id).filter(ForumThread.id == thread_id).first()
    replies = db.session.query(ForumReply, User).join(User, User.id == ForumReply.author_id).filter(ForumReply.thread_id == thread_id).order_by(ForumReply.created_at.asc()).all()
    return render_template("forum_thread.html", course=course, thread=thread, replies=replies)

@bp.post("/courses/<course_id>/forum/<thread_id>/reply")
@login_required
def create_reply(course_id, thread_id):
    body = request.form.get("body")
    thread = db.session.get(ForumThread, thread_id)
    
    reply = ForumReply(
        thread_id=thread_id,
        author_id=current_user.id,
        body=body
    )
    db.session.add(reply)
    db.session.commit()
    
    # Notify thread author if someone else replies
    if thread.author_id != current_user.id:
        notify(
            user_id=thread.author_id,
            type="forum_reply",
            message=f"Có phản hồi mới trong chủ đề '{thread.title}' của bạn.",
            link=url_for("communication.view_thread", course_id=course_id, thread_id=thread_id)
        )
        
    return redirect(url_for("communication.view_thread", course_id=course_id, thread_id=thread_id))

@bp.post("/teacher/forum/<thread_id>/pin")
@login_required
@role_required("teacher")
def pin_thread(thread_id):
    thread = db.session.get(ForumThread, thread_id)
    course = db.session.get(Course, thread.course_id)
    if thread and course.teacher_id == current_user.id:
        thread.is_pinned = not thread.is_pinned
        db.session.commit()
    return redirect(url_for("communication.course_forum", course_id=course.id))

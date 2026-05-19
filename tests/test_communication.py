# -*- coding: utf-8 -*-
import pytest

from e16_app import create_app, db
from e16_app.models import Course, Enrollment, ForumThread, ForumReply, Notification, User


@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_teacher_can_hide_forum_thread(client, app):
    with app.app_context():
        teacher = User(email="mod_teacher@e16.edu.vn", password_hash="hash", role="teacher")
        student = User(email="mod_student@e16.edu.vn", password_hash="hash", role="student")
        db.session.add_all([teacher, student])
        db.session.flush()
        course = Course(title="Moderated", teacher_id=teacher.id, status="published")
        db.session.add(course)
        db.session.flush()
        db.session.add(Enrollment(user_id=student.id, course_id=course.id))
        thread = ForumThread(course_id=course.id, author_id=student.id, title="Bad", body="Hidden")
        db.session.add(thread)
        db.session.commit()
        teacher_id = teacher.id
        course_id = course.id
        thread_id = thread.id

    with client.session_transaction() as sess:
        sess["_user_id"] = teacher_id
        sess["_fresh"] = True

    response = client.post(f"/courses/{course_id}/forum/{thread_id}/hide")

    assert response.status_code == 302
    with app.app_context():
        assert db.session.get(ForumThread, thread_id).is_hidden is True


def test_student_cannot_hide_forum_reply(client, app):
    with app.app_context():
        teacher = User(email="reply_teacher@e16.edu.vn", password_hash="hash", role="teacher")
        student = User(email="reply_student@e16.edu.vn", password_hash="hash", role="student")
        db.session.add_all([teacher, student])
        db.session.flush()
        course = Course(title="Replies", teacher_id=teacher.id, status="published")
        db.session.add(course)
        db.session.flush()
        db.session.add(Enrollment(user_id=student.id, course_id=course.id))
        thread = ForumThread(course_id=course.id, author_id=student.id, title="Thread", body="Body")
        db.session.add(thread)
        db.session.flush()
        reply = ForumReply(thread_id=thread.id, author_id=student.id, body="Reply")
        db.session.add(reply)
        db.session.commit()
        student_id = student.id
        course_id = course.id
        reply_id = reply.id

    with client.session_transaction() as sess:
        sess["_user_id"] = student_id
        sess["_fresh"] = True

    response = client.post(f"/courses/{course_id}/forum/replies/{reply_id}/hide")

    assert response.status_code == 302
    with app.app_context():
        assert db.session.get(ForumReply, reply_id).is_hidden is False


def test_notifications_are_paginated(client, app):
    with app.app_context():
        user = User(email="notif_user@e16.edu.vn", password_hash="hash", role="student")
        db.session.add(user)
        db.session.flush()
        for idx in range(25):
            db.session.add(Notification(user_id=user.id, type="announcement", message=f"Notification {idx}"))
        db.session.commit()
        user_id = user.id

    with client.session_transaction() as sess:
        sess["_user_id"] = user_id
        sess["_fresh"] = True

    response = client.get("/notifications?page=2&per_page=10")

    assert response.status_code == 200
    assert "Trang 2/3".encode("utf-8") in response.data

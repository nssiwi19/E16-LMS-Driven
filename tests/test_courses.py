# -*- coding: utf-8 -*-
import pytest
from e16_app import create_app, db
from e16_app.models import User, Course, Lesson, Enrollment

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False
    })
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def teacher_user(app):
    with app.app_context():
        user = User(email="teacher_test@e16.edu.vn", password_hash="hash", role="teacher")
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def student_user(app):
    with app.app_context():
        user = User(email="student_test@e16.edu.vn", password_hash="hash", role="student")
        db.session.add(user)
        db.session.commit()
        return user

def test_teacher_create_course(client, app, teacher_user):
    with client.session_transaction() as sess:
        sess["_user_id"] = teacher_user.id
        sess["_fresh"] = True
    
    response = client.post("/teacher/courses/new", data={"title": "Test Course 101"})
    assert response.status_code == 302
    
    with app.app_context():
        course = db.session.query(Course).filter_by(title="Test Course 101").first()
        assert course is not None
        assert course.teacher_id == teacher_user.id
        assert course.status == "draft"

def test_student_enrollment(client, app, student_user, teacher_user):
    with app.app_context():
        course = Course(title="Learn Python", teacher_id=teacher_user.id, status="published")
        db.session.add(course)
        db.session.commit()
        course_id = course.id

    with client.session_transaction() as sess:
        sess["_user_id"] = student_user.id
        sess["_fresh"] = True

    response = client.post(f"/student/courses/{course_id}/enroll")
    assert response.status_code == 302

    with app.app_context():
        enrollment = db.session.query(Enrollment).filter_by(user_id=student_user.id, course_id=course_id).first()
        assert enrollment is not None
        assert enrollment.status == "active"

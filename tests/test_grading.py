# -*- coding: utf-8 -*-
import pytest
from e16_app import create_app, db
from e16_app.models import User, Quiz, Question, Choice
from e16_app.services import GradingService

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

def test_quiz_grading(app):
    """Verify that GradingService calculates scores correctly."""
    with app.app_context():
        # Setup dummy data
        u = User(email="s@e16.edu.vn", role="student", password_hash="dummy")
        db.session.add(u)
        db.session.flush()
        
        from e16_app.models import Course
        c = Course(title="Dummy Course", teacher_id=u.id)
        db.session.add(c)
        db.session.flush()
        
        q = Quiz(title="Test Quiz", course_id=c.id, is_published=True)
        db.session.add(q)
        db.session.flush()
        
        qn = Question(quiz_id=q.id, text="1+1=?")
        db.session.add(qn)
        db.session.flush()
        
        c1 = Choice(question_id=qn.id, text="2", is_correct=True)
        c2 = Choice(question_id=qn.id, text="3", is_correct=False)
        db.session.add_all([c1, c2])
        db.session.commit()
        
        # Test Correct Answer
        attempt = GradingService.grade_quiz_attempt(u.id, q.id, {str(qn.id): str(c1.id)})
        assert attempt.score == 100
        
        # Test Wrong Answer
        attempt2 = GradingService.grade_quiz_attempt(u.id, q.id, {str(qn.id): str(c2.id)})
        assert attempt2.score == 0

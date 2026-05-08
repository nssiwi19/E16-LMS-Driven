import csv
import os
from io import StringIO

from e16_app import create_app
from e16_app.models import Course, LearningLog, Lesson, User

app = create_app()


def run():
    seed_password = os.getenv("E16_SEED_PASSWORD")
    if not seed_password:
        raise RuntimeError("E16_SEED_PASSWORD is required for verify.py")

    with app.app_context():
        client = app.test_client()

        seed_res = client.get("/seed")
        print("seed:", seed_res.status_code)
        assert seed_res.status_code in (200, 400)

        student_email = os.getenv("E16_SEED_STUDENT_EMAIL", "student@e16.local")
        admin_email = os.getenv("E16_SEED_ADMIN_EMAIL", "admin@e16.local")

        student_before = User.query.filter_by(email=student_email).first()
        before_login_count = student_before.login_count if student_before else 0
        before_last_login = student_before.last_login if student_before else None

        res = client.post(
            "/login",
            data={"email": student_email, "password": seed_password},
            follow_redirects=False,
        )
        print("student_login:", res.status_code, res.headers.get("Location"))
        assert res.status_code == 302

        course = Course.query.first()
        print("course_exists:", bool(course))
        if not course:
            return

        first_lesson = (
            Lesson.query.filter_by(course_id=course.id).order_by(Lesson.sequence_order.asc()).first()
        )
        assert first_lesson is not None
        before_start_count = (
            LearningLog.query.filter_by(lesson_id=first_lesson.id, action_type="start").count()
        )

        res = client.get(f"/learn/{course.id}", follow_redirects=True)
        print("learn_page:", res.status_code)
        assert res.status_code == 200
        after_start_count = LearningLog.query.filter_by(lesson_id=first_lesson.id, action_type="start").count()
        assert after_start_count >= before_start_count + 1

        before_complete_count = (
            LearningLog.query.filter_by(lesson_id=first_lesson.id, action_type="complete").count()
        )
        res = client.post(f"/learn/{course.id}/complete/{first_lesson.id}", follow_redirects=True)
        print("mark_complete:", res.status_code)
        assert res.status_code == 200
        after_complete_count = (
            LearningLog.query.filter_by(lesson_id=first_lesson.id, action_type="complete").count()
        )
        assert after_complete_count >= before_complete_count + 1

        student_after = User.query.filter_by(email=student_email).first()
        assert student_after is not None
        assert student_after.login_count >= before_login_count + 1
        assert student_after.last_login is not None
        if before_last_login:
            assert student_after.last_login >= before_last_login

        admin_client = app.test_client()
        res = admin_client.post(
            "/login",
            data={"email": admin_email, "password": seed_password},
            follow_redirects=False,
        )
        print("admin_login:", res.status_code, res.headers.get("Location"))
        assert res.status_code == 302

        res = admin_client.get("/analytics")
        print("analytics:", res.status_code)
        assert res.status_code == 200
        assert b"new Chart(" in res.data

        res = admin_client.get("/analytics/export.csv")
        print("csv:", res.status_code, "bytes:", len(res.data))
        assert res.status_code == 200
        rows = list(csv.DictReader(StringIO(res.data.decode("utf-8"))))
        expected = {"student_email", "course_title", "lesson_title", "action_type", "timestamp"}
        assert expected.issubset(set(rows[0].keys()) if rows else expected)
        print("verify: passed all assertions")


if __name__ == "__main__":
    run()

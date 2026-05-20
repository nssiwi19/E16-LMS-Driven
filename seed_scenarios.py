# -*- coding: utf-8 -*-
"""
Database Seeder for E16 LMS Scenario & Edge Cases.
Seeds the exact 11 users, 6 courses, 8 lessons, 8 enrollments, 3 quizzes,
questions, choices, attempts, learning logs, and certificates into the local SQLite database.
All users will have the password: TestPass123!
"""
import os
import sys
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash

from e16_app import create_app
from e16_app.extensions import db
from e16_app.models import (
    User, Course, Lesson, Enrollment, Quiz, Question, Choice, QuizAttempt, LearningLog, Certificate
)

def run_seed():
    app = create_app()
    with app.app_context():
        print("[*] Bat dau nap du lieu mau Scenario & Edge Cases...")
        
        # 1. Tao bang neu chua ton tai
        db.create_all()

        print("[*] Dang don dep du lieu cu de tranh trung lap...")
        try:
            # Xoa sach du lieu cu theo thu tu de khong bi loi khoa ngoai
            db.session.query(Certificate).delete()
            db.session.query(LearningLog).delete()
            db.session.query(QuizAttempt).delete()
            db.session.query(Choice).delete()
            db.session.query(Question).delete()
            db.session.query(Quiz).delete()
            db.session.query(Enrollment).delete()
            db.session.query(Lesson).delete()
            db.session.query(Course).delete()
            db.session.query(User).delete()
            db.session.commit()
            print("[+] Da don dep database thanh cong.")
        except Exception as e:
            db.session.rollback()
            print(f"[-] Khong the tu dong don dep: {str(e)}")

        now = datetime.now(timezone.utc)
        pwd_hash = generate_password_hash("TestPass123!")

        # 2. Them USERS
        print("[*] Dang tao 11 nguoi dung...")
        users = [
            User(id='u-admin', email='admin@e16.local', password_hash=pwd_hash, role='admin', created_at=now - timedelta(days=90), login_count=42, last_login=now),
            User(id='u-ta', email='teacher_a@e16.local', password_hash=pwd_hash, role='teacher', created_at=now - timedelta(days=80), login_count=18, last_login=now),
            User(id='u-tb', email='teacher_b@e16.local', password_hash=pwd_hash, role='teacher', created_at=now - timedelta(days=75), login_count=12, last_login=now),
            User(id='u-s1', email='student_1@e16.local', password_hash=pwd_hash, role='student', created_at=now - timedelta(days=60), login_count=30, last_login=now),
            User(id='u-s2', email='student_2@e16.local', password_hash=pwd_hash, role='student', created_at=now - timedelta(days=55), login_count=15, last_login=now),
            User(id='u-s3', email='student_3@e16.local', password_hash=pwd_hash, role='student', created_at=now - timedelta(days=50), login_count=10, last_login=now),
            User(id='u-s4', email='student_4@e16.local', password_hash=pwd_hash, role='student', created_at=now - timedelta(days=45), login_count=8, last_login=now),
            User(id='u-sd', email='student_done@e16.local', password_hash=pwd_hash, role='student', created_at=now - timedelta(days=70), login_count=50, last_login=now - timedelta(days=5)),
            User(id='u-s5', email='student_5@e16.local', password_hash=pwd_hash, role='student', created_at=now - timedelta(days=10), login_count=2, last_login=now),
            User(id='u-snr', email='student_notenrolled@e16.local', password_hash=pwd_hash, role='student', created_at=now - timedelta(days=5), login_count=1, last_login=now),
            User(id='u-inactive', email='inactive@e16.local', password_hash=pwd_hash, role='student', created_at=now - timedelta(days=30), login_count=3, last_login=now - timedelta(days=30), is_active=False),
        ]
        db.session.add_all(users)
        db.session.commit()

        # 3. Them COURSES
        print("[*] Dang tao 6 khoa hoc...")
        courses = [
            Course(id='c-py', title='Python for Data', description='Khoa hoc Python co ban den nang cao.', cover_image_url='/static/img/course_python.jpg', total_lessons=8, teacher_id='u-ta', created_at=now - timedelta(days=80), status='published'),
            Course(id='c-sql', title='SQL Fundamentals', description='Truy van du lieu voi PostgreSQL.', cover_image_url='/static/img/course_sql.jpg', total_lessons=6, teacher_id='u-ta', created_at=now - timedelta(days=70), status='published'),
            Course(id='c-draft', title='Data Viz (Draft)', description='Dang soan thao, chua publish.', cover_image_url='/static/img/placeholder.jpg', total_lessons=0, teacher_id='u-ta', created_at=now - timedelta(days=10), status='draft'),
            Course(id='c-pend', title='Statistics Basics', description='Cho admin duyet.', cover_image_url='/static/img/placeholder.jpg', total_lessons=5, teacher_id='u-tb', created_at=now - timedelta(days=5), status='pending_review'),
            Course(id='c-del', title='Deleted Course', description='Khoa hoc da bi xoa mem.', cover_image_url='/static/img/placeholder.jpg', total_lessons=3, teacher_id='u-tb', created_at=now - timedelta(days=60), status='archived', is_deleted=True),
            Course(id='c-tb', title='Teacher B Course', description='Khoa hoc cua teacher B.', cover_image_url='/static/img/placeholder.jpg', total_lessons=4, teacher_id='u-tb', created_at=now - timedelta(days=40), status='published'),
        ]
        db.session.add_all(courses)
        db.session.commit()

        # 4. Them LESSONS
        print("[*] Dang tao 8 bai hoc cho khoa Python...")
        lessons = [
            Lesson(id='l-1', course_id='c-py', title='Gioi thieu Python', video_url='https://example.com/v1', document_url='https://example.com/d1', sequence_order=1, created_at=now - timedelta(days=79)),
            Lesson(id='l-2', course_id='c-py', title='Kieu du lieu co ban', video_url='https://example.com/v2', document_url='https://example.com/d2', sequence_order=2, created_at=now - timedelta(days=78)),
            Lesson(id='l-3', course_id='c-py', title='Vong lap va dieu kien', video_url='https://example.com/v3', document_url='https://example.com/d3', sequence_order=3, created_at=now - timedelta(days=77)),
            Lesson(id='l-4', course_id='c-py', title='Ham va module', video_url='https://example.com/v4', document_url='https://example.com/d4', sequence_order=4, created_at=now - timedelta(days=76)),
            Lesson(id='l-5', course_id='c-py', title='List, Dict, Set', video_url='https://example.com/v5', document_url='https://example.com/d5', sequence_order=5, created_at=now - timedelta(days=75)),
            Lesson(id='l-6', course_id='c-py', title='File I/O', video_url='https://example.com/v6', document_url='https://example.com/d6', sequence_order=6, created_at=now - timedelta(days=74)),
            Lesson(id='l-7', course_id='c-py', title='Xu ly exception', video_url='https://example.com/v7', document_url='https://example.com/d7', sequence_order=7, created_at=now - timedelta(days=73)),
            Lesson(id='l-8', course_id='c-py', title='Project thuc hanh', video_url='https://example.com/v8', document_url='https://example.com/d8', sequence_order=8, created_at=now - timedelta(days=72)),
        ]
        db.session.add_all(lessons)
        db.session.commit()

        # 5. Them ENROLLMENTS
        print("[*] Dang tao cac ban ghi dang ky hoc...")
        enrollments = [
            Enrollment(id='e-s1-py', user_id='u-s1', course_id='c-py', enrolled_at=now - timedelta(days=58), status='active'),
            Enrollment(id='e-s2-py', user_id='u-s2', course_id='c-py', enrolled_at=now - timedelta(days=50), status='active'),
            Enrollment(id='e-s3-py', user_id='u-s3', course_id='c-py', enrolled_at=now - timedelta(days=40), status='active'),
            Enrollment(id='e-s4-py', user_id='u-s4', course_id='c-py', enrolled_at=now - timedelta(days=30), status='active'),
            Enrollment(id='e-sd-py', user_id='u-sd', course_id='c-py', enrolled_at=now - timedelta(days=68), status='completed'),
            Enrollment(id='e-s5-py', user_id='u-s5', course_id='c-py', enrolled_at=now - timedelta(days=8), status='pending_payment'),
            Enrollment(id='e-s1-sql', user_id='u-s1', course_id='c-sql', enrolled_at=now - timedelta(days=45), status='active'),
            Enrollment(id='e-sd-sql', user_id='u-sd', course_id='c-sql', enrolled_at=now - timedelta(days=60), status='completed'),
        ]
        db.session.add_all(enrollments)
        db.session.commit()

        # 6. Them QUIZZES
        print("[*] Dang tao cac bai trac nghiem...")
        quizzes = [
            Quiz(id='qz-1', course_id='c-py', title='Quiz cuoi khoa Python', pass_score=80, max_attempts=3, due_date=None, is_published=True, created_at=now - timedelta(days=70)),
            Quiz(id='qz-2', course_id='c-py', title='Quiz giua ky', pass_score=70, max_attempts=2, due_date=now - timedelta(days=5), is_published=True, created_at=now - timedelta(days=70)),
            Quiz(id='qz-3', course_id='c-py', title='Quiz nhap', pass_score=80, max_attempts=1, due_date=None, is_published=False, created_at=now - timedelta(days=5)),
        ]
        db.session.add_all(quizzes)
        db.session.commit()

        # 7. Them QUESTIONS & CHOICES
        print("[*] Dang tao cau hoi va dap an...")
        questions = [
            Question(id='q-1', quiz_id='qz-1', text='Python duoc tao boi ai?', q_type='mcq', sequence_order=1),
            Question(id='q-2', quiz_id='qz-1', text='Kieu du lieu nao la immutable trong Python?', q_type='mcq', sequence_order=2),
            Question(id='q-3', quiz_id='qz-1', text='Ket qua cua 2**10 la bao nhieu?', q_type='mcq', sequence_order=3),
        ]
        db.session.add_all(questions)
        db.session.commit()

        choices = [
            Choice(id='ch-1-1', question_id='q-1', text='Guido van Rossum', is_correct=True),
            Choice(id='ch-1-2', question_id='q-1', text='Linus Torvalds', is_correct=False),
            Choice(id='ch-1-3', question_id='q-1', text='James Gosling', is_correct=False),
            Choice(id='ch-2-1', question_id='q-2', text='list', is_correct=False),
            Choice(id='ch-2-2', question_id='q-2', text='tuple', is_correct=True),
            Choice(id='ch-2-3', question_id='q-2', text='dict', is_correct=False),
            Choice(id='ch-3-1', question_id='q-3', text='512', is_correct=False),
            Choice(id='ch-3-2', question_id='q-3', text='1024', is_correct=True),
            Choice(id='ch-3-3', question_id='q-3', text='256', is_correct=False),
        ]
        db.session.add_all(choices)
        db.session.commit()

        # 8. Them QUIZ ATTEMPTS
        print("[*] Dang tao cac luot lam bai...")
        attempts = [
            QuizAttempt(id='qa-s1-1', quiz_id='qz-1', user_id='u-s1', score=90, passed=True, attempted_at=now - timedelta(days=20), completed_at=now - timedelta(days=20) + timedelta(minutes=25)),
            QuizAttempt(id='qa-s2-1', quiz_id='qz-1', user_id='u-s2', score=50, passed=False, attempted_at=now - timedelta(days=25), completed_at=now - timedelta(days=25) + timedelta(minutes=30)),
            QuizAttempt(id='qa-s2-2', quiz_id='qz-1', user_id='u-s2', score=55, passed=False, attempted_at=now - timedelta(days=20), completed_at=now - timedelta(days=20) + timedelta(minutes=28)),
            QuizAttempt(id='qa-s2-3', quiz_id='qz-1', user_id='u-s2', score=60, passed=False, attempted_at=now - timedelta(days=15), completed_at=now - timedelta(days=15) + timedelta(minutes=32)),
            QuizAttempt(id='qa-s3-1', quiz_id='qz-1', user_id='u-s3', score=None, passed=None, attempted_at=now - timedelta(hours=1), completed_at=None),
            QuizAttempt(id='qa-sd-1', quiz_id='qz-1', user_id='u-sd', score=95, passed=True, attempted_at=now - timedelta(days=60), completed_at=now - timedelta(days=60) + timedelta(minutes=20)),
        ]
        db.session.add_all(attempts)
        db.session.commit()

        # 9. Them LEARNING LOGS
        print("[*] Dang tao lich su hoc tap...")
        logs = [
            LearningLog(log_id='ll-sd-1-s', user_id='u-sd', lesson_id='l-1', action_type='start', timestamp=now - timedelta(days=68)),
            LearningLog(log_id='ll-sd-1-c', user_id='u-sd', lesson_id='l-1', action_type='complete', timestamp=now - timedelta(days=68) + timedelta(minutes=45)),
            LearningLog(log_id='ll-sd-2-s', user_id='u-sd', lesson_id='l-2', action_type='start', timestamp=now - timedelta(days=67)),
            LearningLog(log_id='ll-sd-2-c', user_id='u-sd', lesson_id='l-2', action_type='complete', timestamp=now - timedelta(days=67) + timedelta(minutes=50)),
            LearningLog(log_id='ll-sd-3-c', user_id='u-sd', lesson_id='l-3', action_type='complete', timestamp=now - timedelta(days=65)),
            LearningLog(log_id='ll-sd-4-c', user_id='u-sd', lesson_id='l-4', action_type='complete', timestamp=now - timedelta(days=63)),
            LearningLog(log_id='ll-sd-5-c', user_id='u-sd', lesson_id='l-5', action_type='complete', timestamp=now - timedelta(days=60)),
            LearningLog(log_id='ll-sd-6-c', user_id='u-sd', lesson_id='l-6', action_type='complete', timestamp=now - timedelta(days=57)),
            LearningLog(log_id='ll-sd-7-c', user_id='u-sd', lesson_id='l-7', action_type='complete', timestamp=now - timedelta(days=52)),
            LearningLog(log_id='ll-sd-8-c', user_id='u-sd', lesson_id='l-8', action_type='complete', timestamp=now - timedelta(days=48)),

            LearningLog(log_id='ll-s1-1', user_id='u-s1', lesson_id='l-1', action_type='complete', timestamp=now - timedelta(days=57)),
            LearningLog(log_id='ll-s1-2', user_id='u-s1', lesson_id='l-2', action_type='complete', timestamp=now - timedelta(days=57) + timedelta(hours=2)),
            LearningLog(log_id='ll-s1-3', user_id='u-s1', lesson_id='l-3', action_type='complete', timestamp=now - timedelta(days=57) + timedelta(hours=4)),
            LearningLog(log_id='ll-s1-4', user_id='u-s1', lesson_id='l-4', action_type='complete', timestamp=now - timedelta(days=56)),
            LearningLog(log_id='ll-s1-5', user_id='u-s1', lesson_id='l-5', action_type='complete', timestamp=now - timedelta(days=56) + timedelta(hours=3)),
            LearningLog(log_id='ll-s1-6', user_id='u-s1', lesson_id='l-6', action_type='start', timestamp=now - timedelta(days=10)),

            LearningLog(log_id='ll-s2-1', user_id='u-s2', lesson_id='l-1', action_type='complete', timestamp=now - timedelta(days=48)),
            LearningLog(log_id='ll-s2-2', user_id='u-s2', lesson_id='l-2', action_type='complete', timestamp=now - timedelta(days=46)),

            LearningLog(log_id='ll-s3-1', user_id='u-s3', lesson_id='l-1', action_type='complete', timestamp=now - timedelta(days=38)),
            LearningLog(log_id='ll-s3-2', user_id='u-s3', lesson_id='l-2', action_type='complete', timestamp=now - timedelta(days=36)),
            LearningLog(log_id='ll-s3-3', user_id='u-s3', lesson_id='l-3', action_type='complete', timestamp=now - timedelta(days=33)),

            LearningLog(log_id='ll-s4-1', user_id='u-s4', lesson_id='l-1', action_type='complete', timestamp=now - timedelta(days=28)),
        ]
        db.session.add_all(logs)
        db.session.commit()

        # 10. Them CERTIFICATE
        print("[*] Dang tao chung chi...")
        cert = Certificate(id='cert-done-py', user_id='u-sd', course_id='c-py', cert_code='cert-code-sd-py', issued_at=now - timedelta(days=48))
        db.session.add(cert)
        db.session.commit()

        print("\n[+] HOAN THANH NAP DU LIEU MAU THANH CONG!")
        print("-----------------------------------------------------------------")
        print("Tai khoan dang nhap cuc bo:")
        print("MAT KHAU CHUNG: TestPass123!")
        print("-----------------------------------------------------------------")
        print("1. Admin:           admin@e16.local")
        print("2. Giao vien A:     teacher_a@e16.local")
        print("3. Giao vien B:     teacher_b@e16.local")
        print("4. Hoc vien 1:      student_1@e16.local")
        print("5. Hoc vien 2:      student_2@e16.local")
        print("6. Hoc vien 3:      student_3@e16.local")
        print("7. Hoc vien Done:   student_done@e16.local")
        print("8. Hoc vien Chua TT: student_5@e16.local")
        print("9. Hoc vien Khong DK: student_notenrolled@e16.local")
        print("10. Tai khoan khoa: inactive@e16.local")
        print("-----------------------------------------------------------------")

if __name__ == "__main__":
    run_seed()

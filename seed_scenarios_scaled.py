# -*- coding: utf-8 -*-
"""
Scaled Database Seeder for E16 LMS Scenario & Edge Cases.
Scales up database size by 100x while strictly preserving the 11 core scenario users,
distributing all entities and actions dynamically across the last 90 days.
Generates realistic, sequential, start-to-complete learning logs for students.
"""
import os
import sys
import random
import uuid
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash

from e16_app import create_app
from e16_app.extensions import db
from e16_app.models import (
    User, Course, Lesson, Enrollment, Quiz, Question, Choice, QuizAttempt, LearningLog, Certificate
)

def run_scaled_seed():
    app = create_app()
    with app.app_context():
        print("[*] Bat dau nap du lieu mau quy mo lon (100x Scaled) cho E16 LMS...")
        
        # 1. Tao bang neu chua ton tai
        db.create_all()

        print("[*] Dang don dep du lieu cu de tranh trung lap...")
        try:
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

        now = datetime.utcnow()
        pwd_hash = generate_password_hash("TestPass123!")

        # ==========================================
        # 2. CORE SCENARIO USERS (Strictly Preserved)
        # ==========================================
        print("[*] Dang tao 11 nguoi dung kich ban loi...")
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

        # ==========================================
        # 3. EXTRA SCALED USERS (100x Scale = 1,100 users)
        # ==========================================
        print("[*] Dang tao 1100 hoc vien ngau nhien (Phan bo 90 ngay)...")
        scaled_users = []
        # Create an increasing registration pattern over the last 90 days (exponential growth)
        for i in range(1100):
            # Squaring a random float pushes the distribution towards recent days (growth curve!)
            days_ago = int(90 * (random.random() ** 1.5))
            reg_time = now - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
            
            uid = f"u-gen-{i}"
            email = f"student_gen_{i}@e16.local"
            last_log = reg_time + timedelta(days=random.randint(0, max(0, (now - reg_time).days)))
            
            scaled_users.append(User(
                id=uid,
                email=email,
                password_hash=pwd_hash,
                role='student',
                created_at=reg_time,
                login_count=random.randint(1, 40),
                last_login=last_log,
                is_active=True
            ))
        db.session.add_all(scaled_users)
        db.session.commit()
        print("[+] Da tao 1100 hoc vien bo sung.")

        # ==========================================
        # 4. CORE COURSES
        # ==========================================
        print("[*] Dang tao 6 khoa hoc kich ban...")
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

        # ==========================================
        # 5. EXTRA SCALED COURSES (24 new courses, total 30)
        # ==========================================
        print("[*] Dang tao 24 khoa hoc bo sung...")
        course_topics = [
            "Javascript Essentials", "HTML5 & CSS3 Responsive", "React Native Mobile Dev", "DevOps and CI/CD Pipelines",
            "Docker & Kubernetes Containerization", "Node.js Backend Architecture", "Machine Learning with Scikit-Learn",
            "Deep Learning & PyTorch Basics", "Data Analysis with Pandas", "Excel for Business Intelligence",
            "Product Management Fundamentals", "Agile & Scrum Practices", "SEO & Content Marketing Strategy",
            "Facebook Ads Mastery", "Google Analytics 4 Overview", "Cybersecurity Essentials",
            "Ethical Hacking Foundations", "AWS Cloud Practitioner Prep", "PostgreSQL Advanced Performance",
            "MongoDB & NoSQL Databases", "Rust Programming Fundamentals", "Go Web Development",
            "SwiftUI iOS Development", "UI/UX Figma Design Mastery"
        ]
        
        scaled_courses = []
        for idx, topic in enumerate(course_topics):
            cid = f"c-gen-{idx}"
            days_ago = random.randint(30, 85)
            c_created = now - timedelta(days=days_ago)
            teacher = 'u-ta' if idx % 2 == 0 else 'u-tb'
            total_l = random.randint(5, 12)
            
            scaled_courses.append(Course(
                id=cid,
                title=topic,
                description=f"Khoa hoc chuyen sau ve {topic} phu hop cho moi doi tuong.",
                cover_image_url='/static/img/placeholder.jpg',
                total_lessons=total_l,
                teacher_id=teacher,
                created_at=c_created,
                status='published'
            ))
        db.session.add_all(scaled_courses)
        db.session.commit()
        print("[+] Da tao 24 khoa hoc bo sung.")

        # ==========================================
        # 6. LESSONS FOR ALL COURSES
        # ==========================================
        print("[*] Dang tao bai hoc cho tat ca khoa hoc...")
        # Add 8 core lessons for c-py
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
        
        # Add 6 lessons for c-sql
        for i in range(1, 7):
            lessons.append(Lesson(id=f"l-sql-{i}", course_id="c-sql", title=f"Bai {i}: Truyen van SQL", sequence_order=i, created_at=now - timedelta(days=69)))
            
        # Add lessons for generated courses
        all_lessons_map = {} # cid -> list of lesson objects
        all_lessons_map['c-py'] = lessons[:8]
        all_lessons_map['c-sql'] = lessons[8:14]
        
        for c in scaled_courses:
            all_lessons_map[c.id] = []
            for l_idx in range(1, c.total_lessons + 1):
                lid = f"l-gen-{c.id}-{l_idx}"
                l = Lesson(
                    id=lid,
                    course_id=c.id,
                    title=f"Bai {l_idx}: Noi dung thuc hanh",
                    video_url="https://example.com/video",
                    document_url="https://example.com/doc",
                    sequence_order=l_idx,
                    created_at=c.created_at + timedelta(days=1)
                )
                lessons.append(l)
                all_lessons_map[c.id].append(l)
                
        db.session.add_all(lessons)
        db.session.commit()
        print(f"[+] Da tao tong cong {len(lessons)} bai hoc.")

        # ==========================================
        # 7. ENROLLMENTS & QUIZZES
        # ==========================================
        print("[*] Dang tao enrollments va quizzes...")
        # Core enrollments
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

        # Scaled Quizzes for generated courses
        quizzes = [
            Quiz(id='qz-1', course_id='c-py', title='Quiz cuoi khoa Python', pass_score=80, max_attempts=3, due_date=None, is_published=True, created_at=now - timedelta(days=70)),
            Quiz(id='qz-2', course_id='c-py', title='Quiz giua ky', pass_score=70, max_attempts=2, due_date=now - timedelta(days=5), is_published=True, created_at=now - timedelta(days=70)),
            Quiz(id='qz-3', course_id='c-py', title='Quiz nhap', pass_score=80, max_attempts=1, due_date=None, is_published=False, created_at=now - timedelta(days=5)),
        ]

        for c in scaled_courses:
            qid = f"qz-gen-{c.id}"
            quizzes.append(Quiz(
                id=qid,
                course_id=c.id,
                title=f"Quiz cuoi khoa {c.title}",
                pass_score=80,
                max_attempts=3,
                due_date=None,
                is_published=True,
                created_at=c.created_at + timedelta(days=2)
            ))

        db.session.add_all(quizzes)
        db.session.commit()

        # Questions & Choices for qz-1
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

        # Questions and Choices for generated quizzes (so exports don't crash)
        gen_questions = []
        gen_choices = []
        for qz in quizzes:
            if qz.id == 'qz-1' or qz.id == 'qz-2' or qz.id == 'qz-3':
                continue
            # 1 simple question per generated quiz
            qn_id = f"q-gen-{qz.id}"
            gen_questions.append(Question(id=qn_id, quiz_id=qz.id, text="Cau hoi trac nghiem co ban?", q_type="mcq", sequence_order=1))
            gen_choices.append(Choice(id=f"ch-gen-{qz.id}-1", question_id=qn_id, text="Dap an A (Dung)", is_correct=True))
            gen_choices.append(Choice(id=f"ch-gen-{qz.id}-2", question_id=qn_id, text="Dap an B (Sai)", is_correct=False))

        db.session.add_all(gen_questions)
        db.session.add_all(gen_choices)
        db.session.commit()

        # ==========================================
        # 8. EXTRA SCALED ENROLLMENTS (900+ registrations)
        # ==========================================
        print("[*] Dang tao 900 dang ky hoc (Bieu do tang truong 90 ngay)...")
        all_active_courses = [c for c in courses if c.status == 'published' and not c.is_deleted] + scaled_courses
        
        scaled_enrollments = []
        # Assign random courses to users
        enroll_count = 0
        for u in scaled_users:
            # Randomly register each student to 1-3 courses
            registered_courses = random.sample(all_active_courses, random.randint(1, 2))
            for c in registered_courses:
                eid = f"e-gen-{enroll_count}"
                
                # Enrollment date must be after user created_at
                max_days = (now - u.created_at).days
                days_since_reg = random.randint(0, max(0, max_days))
                enroll_date = u.created_at + timedelta(days=days_since_reg, hours=random.randint(0, 23))
                
                status = random.choice(['active', 'active', 'completed', 'completed', 'pending_payment'])
                
                scaled_enrollments.append(Enrollment(
                    id=eid,
                    user_id=u.id,
                    course_id=c.id,
                    enrolled_at=enroll_date,
                    status=status
                ))
                enroll_count += 1
                
        db.session.add_all(scaled_enrollments)
        db.session.commit()
        print(f"[+] Da tao {len(scaled_enrollments)} dang ky hoc bo sung.")

        # ==========================================
        # 9. SCALED ATTEMPTS & CERTIFICATES
        # ==========================================
        print("[*] Dang tao quiz attempts cho cac hoc vien...")
        attempts = [
            QuizAttempt(id='qa-s1-1', quiz_id='qz-1', user_id='u-s1', score=90, passed=True, attempted_at=now - timedelta(days=20), completed_at=now - timedelta(days=20) + timedelta(minutes=25)),
            QuizAttempt(id='qa-s2-1', quiz_id='qz-1', user_id='u-s2', score=50, passed=False, attempted_at=now - timedelta(days=25), completed_at=now - timedelta(days=25) + timedelta(minutes=30)),
            QuizAttempt(id='qa-s2-2', quiz_id='qz-1', user_id='u-s2', score=55, passed=False, attempted_at=now - timedelta(days=20), completed_at=now - timedelta(days=20) + timedelta(minutes=28)),
            QuizAttempt(id='qa-s2-3', quiz_id='qz-1', user_id='u-s2', score=60, passed=False, attempted_at=now - timedelta(days=15), completed_at=now - timedelta(days=15) + timedelta(minutes=32)),
            QuizAttempt(id='qa-s3-1', quiz_id='qz-1', user_id='u-s3', score=None, passed=None, attempted_at=now - timedelta(hours=1), completed_at=None),
            QuizAttempt(id='qa-sd-1', quiz_id='qz-1', user_id='u-sd', score=95, passed=True, attempted_at=now - timedelta(days=60), completed_at=now - timedelta(days=60) + timedelta(minutes=20)),
        ]

        # Generate random quiz attempts for completed/active enrollments
        qa_count = 0
        certificates = [
            Certificate(id='cert-done-py', user_id='u-sd', course_id='c-py', cert_code='cert-code-sd-py', issued_at=now - timedelta(days=48))
        ]
        
        for e in scaled_enrollments:
            if e.status in ['active', 'completed']:
                # See if there's a quiz for this course
                c_quiz = next((q for q in quizzes if q.course_id == e.course_id), None)
                if c_quiz:
                    # Completed enrollments always pass, active may pass or fail
                    is_completed = e.status == 'completed'
                    score = random.randint(80, 100) if is_completed else random.randint(40, 95)
                    passed = score >= c_quiz.pass_score
                    
                    attempt_time = e.enrolled_at + timedelta(days=random.randint(1, max(1, (now - e.enrolled_at).days - 1)))
                    
                    attempts.append(QuizAttempt(
                        id=f"qa-gen-{qa_count}",
                        quiz_id=c_quiz.id,
                        user_id=e.user_id,
                        score=score,
                        passed=passed,
                        attempted_at=attempt_time,
                        completed_at=attempt_time + timedelta(minutes=random.randint(10, 40))
                    ))
                    
                    # Generate certificates for completed ones!
                    if is_completed and passed:
                        certificates.append(Certificate(
                            id=f"cert-gen-{qa_count}",
                            user_id=e.user_id,
                            course_id=e.course_id,
                            cert_code=f"cert-code-gen-{qa_count}",
                            issued_at=attempt_time + timedelta(minutes=45)
                        ))
                        
                    qa_count += 1

        db.session.add_all(attempts)
        db.session.add_all(certificates)
        db.session.commit()
        print(f"[+] Da tao {len(attempts)} quiz attempts va {len(certificates)} chung chi.")

        # ==========================================
        # 10. SCALED LEARNING LOGS (Sequential start/complete actions)
        # ==========================================
        print("[*] Dang tao lich su hoc tap tuan tu (Learning Logs)...")
        logs = [
            # student_done — học xong tất cả (time-to-complete ~20 ngày)
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

            # student_1 — học L1-L5 xong, L6 đang dở (time ~2 ngày → binge learner)
            LearningLog(log_id='ll-s1-1', user_id='u-s1', lesson_id='l-1', action_type='complete', timestamp=now - timedelta(days=57)),
            LearningLog(log_id='ll-s1-2', user_id='u-s1', lesson_id='l-2', action_type='complete', timestamp=now - timedelta(days=57) + timedelta(hours=2)),
            LearningLog(log_id='ll-s1-3', user_id='u-s1', lesson_id='l-3', action_type='complete', timestamp=now - timedelta(days=57) + timedelta(hours=4)),
            LearningLog(log_id='ll-s1-4', user_id='u-s1', lesson_id='l-4', action_type='complete', timestamp=now - timedelta(days=56)),
            LearningLog(log_id='ll-s1-5', user_id='u-s1', lesson_id='l-5', action_type='complete', timestamp=now - timedelta(days=56) + timedelta(hours=3)),
            LearningLog(log_id='ll-s1-6', user_id='u-s1', lesson_id='l-6', action_type='start', timestamp=now - timedelta(days=10)),

            # student_2 — học L1-L2 rồi drop
            LearningLog(log_id='ll-s2-1', user_id='u-s2', lesson_id='l-1', action_type='complete', timestamp=now - timedelta(days=48)),
            LearningLog(log_id='ll-s2-2', user_id='u-s2', lesson_id='l-2', action_type='complete', timestamp=now - timedelta(days=46)),

            # student_3 — học L1-L3
            LearningLog(log_id='ll-s3-1', user_id='u-s3', lesson_id='l-1', action_type='complete', timestamp=now - timedelta(days=38)),
            LearningLog(log_id='ll-s3-2', user_id='u-s3', lesson_id='l-2', action_type='complete', timestamp=now - timedelta(days=36)),
            LearningLog(log_id='ll-s3-3', user_id='u-s3', lesson_id='l-3', action_type='complete', timestamp=now - timedelta(days=33)),

            # student_4 — chỉ học L1 (L1 drop-off)
            LearningLog(log_id='ll-s4-1', user_id='u-s4', lesson_id='l-1', action_type='complete', timestamp=now - timedelta(days=28)),
        ]

        # Generate realistic sequential logs for scaled active/completed enrollments
        # To comply with sequential start/complete logs:
        # For each student's enrollment in a course:
        # - They start and complete Lesson 1, then Lesson 2, etc.
        # - Complete action time is always > start action time.
        # - Logs are spread sequentially across days.
        log_index = 0
        for e in scaled_enrollments:
            if e.status in ['active', 'completed']:
                c_lessons = all_lessons_map.get(e.course_id, [])
                if not c_lessons:
                    continue
                
                # Completed students study all lessons. Active students study a random subset.
                num_studied = len(c_lessons) if e.status == 'completed' else random.randint(1, max(1, len(c_lessons) - 1))
                studied_lessons = c_lessons[:num_studied]
                
                current_time = e.enrolled_at + timedelta(hours=random.randint(1, 4))
                
                for idx, les in enumerate(studied_lessons):
                    # For each lesson, write 'start' and 'complete' logs
                    start_time = current_time + timedelta(days=idx * random.randint(1, 3), hours=random.randint(0, 4))
                    complete_time = start_time + timedelta(minutes=random.randint(15, 50))
                    
                    if complete_time > now:
                        break # Prevent logs in the future
                        
                    logs.append(LearningLog(
                        log_id=f"ll-gen-{log_index}-s",
                        user_id=e.user_id,
                        lesson_id=les.id,
                        action_type='start',
                        timestamp=start_time
                    ))
                    
                    logs.append(LearningLog(
                        log_id=f"ll-gen-{log_index}-c",
                        user_id=e.user_id,
                        lesson_id=les.id,
                        action_type='complete',
                        timestamp=complete_time
                    ))
                    
                    log_index += 1
                    current_time = complete_time
                    
        db.session.add_all(logs)
        db.session.commit()
        print(f"[+] Da tao {len(logs)} nhat ky hoc tap tuan tu (Learning Logs).")

        print("\n[+] HOAN THANH NAP QUY MO DU LIEU (100x SCALED) THANH CONG!")
        print("-----------------------------------------------------------------")
        print("Quy mo du lieu moi:")
        print(f"- Nguoi dung:       {db.session.query(User).count()} (Hoc vien bo sung: 1100)")
        print(f"- Khoa hoc:         {db.session.query(Course).count()} (Published: 30)")
        print(f"- Bai hoc:          {db.session.query(Lesson).count()} bai hoc")
        print(f"- Dang ky hoc:      {db.session.query(Enrollment).count()} luot")
        print(f"- Nhat ky hoc tap:  {db.session.query(LearningLog).count()} logs")
        print(f"- Chung chi:        {db.session.query(Certificate).count()} chung chi cap ra")
        print("-----------------------------------------------------------------")
        print("Luu y: Tat ca 11 tai khoan kich ban goc van duoc giu nguyen ven.")
        print("-----------------------------------------------------------------")

if __name__ == "__main__":
    run_scaled_seed()

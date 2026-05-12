import os
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

from e16_app import create_app
from e16_app.extensions import db
from e16_app.models import User, Course, Lesson, Enrollment, LearningLog

app = create_app()

def run_seed():
    with app.app_context():
        # 1. Thêm cột phone vào bảng users nếu chưa có (cho SQLite)
        try:
            db.session.execute(db.text("ALTER TABLE users ADD COLUMN phone VARCHAR(20)"))
            db.session.commit()
            print("Đã thêm cột 'phone' vào bảng users.")
        except Exception as e:
            # Bỏ qua nếu cột đã tồn tại
            db.session.rollback()
            print("Cột 'phone' đã tồn tại hoặc có lỗi:", e)

        # 2. Tạo 1 giáo viên
        teacher = User.query.filter_by(email="teacher_demo@e16.edu.vn").first()
        if not teacher:
            teacher = User(
                email="teacher_demo@e16.edu.vn",
                password_hash=generate_password_hash("123456"),
                role="teacher",
                phone="0988000111"
            )
            db.session.add(teacher)
            db.session.commit()
            print("Đã tạo teacher_demo@e16.edu.vn")

        # 3. Tạo 1 khóa học mẫu
        course = Course.query.filter_by(title="Khóa học Lập trình Web Fullstack 2026").first()
        if not course:
            course = Course(
                title="Khóa học Lập trình Web Fullstack 2026",
                teacher_id=teacher.id,
                status="published",
                total_lessons=10
            )
            db.session.add(course)
            db.session.commit()
            print("Đã tạo Khóa học mẫu")

            # Tạo 10 bài học cho khóa
            lessons = []
            for i in range(1, 11):
                lesson = Lesson(
                    course_id=course.id,
                    title=f"Bài {i}: Kiến thức trọng tâm {i}",
                    sequence_order=i
                )
                db.session.add(lesson)
                lessons.append(lesson)
            db.session.commit()
            print("Đã tạo 10 bài học mẫu")
        else:
            lessons = Lesson.query.filter_by(course_id=course.id).all()

        # 4. Tạo 100 học viên mẫu
        print("Đang tạo 100 học viên...")
        existing_count = User.query.filter(User.email.like("student_demo_%")).count()
        if existing_count < 100:
            for i in range(existing_count + 1, 101):
                phone_num = f"09{random.randint(10000000, 99999999)}"
                student = User(
                    email=f"student_demo_{i}@e16.edu.vn",
                    password_hash=generate_password_hash("123456"),
                    role="student",
                    phone=phone_num
                )
                db.session.add(student)
                
                # Bắt buộc flush để lấy student.id
                db.session.flush()

                # Enroll vào khóa học
                enrollment = Enrollment(
                    user_id=student.id,
                    course_id=course.id,
                    status="active"
                )
                db.session.add(enrollment)

                # Random tiến độ học tập (từ 0 đến 10 bài)
                completed_count = random.randint(0, 10)
                if completed_count == 10:
                    enrollment.status = "completed"

                for j in range(completed_count):
                    log = LearningLog(
                        user_id=student.id,
                        lesson_id=lessons[j].id,
                        action_type="complete"
                    )
                    db.session.add(log)
            
            db.session.commit()
            print("Tạo 100 học viên thành công!")
        else:
            print("Đã có sẵn 100 học viên.")

if __name__ == "__main__":
    run_seed()

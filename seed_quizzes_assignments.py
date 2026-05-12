import os
import random
from e16_app import create_app
from e16_app.extensions import db
from e16_app.models import User, Course, Quiz, Question, Choice, QuizAttempt, Assignment, Submission

app = create_app()

def seed_content():
    with app.app_context():
        # Lấy khóa học mẫu đã tạo từ seed_100.py
        course = Course.query.filter_by(title="Khóa học Lập trình Web Fullstack 2026").first()
        if not course:
            print("Không tìm thấy khóa học mẫu. Bạn cần chạy seed_100.py trước.")
            return

        print("1. Tạo Quiz mẫu...")
        # Tạo 1 Quiz
        quiz = Quiz.query.filter_by(title="Bài kiểm tra giữa khóa", course_id=course.id).first()
        if not quiz:
            quiz = Quiz(
                course_id=course.id,
                title="Bài kiểm tra giữa khóa",
                pass_score=80,
                max_attempts=3,
                is_published=True
            )
            db.session.add(quiz)
            db.session.commit()

            # Tạo các câu hỏi
            questions_data = [
                {
                    "text": "HTML là viết tắt của từ gì?",
                    "choices": [
                        ("Hyper Text Markup Language", True),
                        ("High Text Machine Language", False),
                        ("Hyperlink and Text Markup Language", False)
                    ]
                },
                {
                    "text": "Thẻ nào sau đây dùng để tạo tiêu đề lớn nhất trong HTML?",
                    "choices": [
                        ("<h1>", True),
                        ("<header>", False),
                        ("<heading>", False),
                        ("<h6>", False)
                    ]
                },
                {
                    "text": "Đâu là một thuộc tính dùng để thay đổi màu chữ trong CSS?",
                    "choices": [
                        ("color", True),
                        ("font-color", False),
                        ("text-color", False),
                        ("background-color", False)
                    ]
                }
            ]

            for q_data in questions_data:
                question = Question(quiz_id=quiz.id, text=q_data["text"], q_type="mcq")
                db.session.add(question)
                db.session.flush() # Để có question.id
                
                for text, is_correct in q_data["choices"]:
                    choice = Choice(question_id=question.id, text=text, is_correct=is_correct)
                    db.session.add(choice)

            db.session.commit()
            print("Đã tạo Quiz và 3 câu hỏi trắc nghiệm.")
        else:
            print("Quiz mẫu đã tồn tại.")


        print("2. Tạo Assignment mẫu...")
        assignment = Assignment.query.filter_by(title="Bài tập thực hành: Xây dựng Landing Page", course_id=course.id).first()
        if not assignment:
            assignment = Assignment(
                course_id=course.id,
                title="Bài tập thực hành: Xây dựng Landing Page",
                description="Hãy dùng HTML và CSS để xây dựng một landing page giới thiệu bản thân.",
                allow_file=True,
                allow_text=True
            )
            db.session.add(assignment)
            db.session.commit()
            print("Đã tạo Bài tập (Assignment).")
        else:
            print("Bài tập mẫu đã tồn tại.")

        
        print("3. Giả lập điểm số cho học viên...")
        students = User.query.filter(User.email.like("student_demo_%")).all()
        
        quiz_attempt_count = 0
        submission_count = 0
        
        for student in students:
            # 50% học viên làm quiz
            if random.random() > 0.5:
                existing_attempt = QuizAttempt.query.filter_by(user_id=student.id, quiz_id=quiz.id).first()
                if not existing_attempt:
                    score = random.choice([60, 80, 100]) # Giả lập điểm
                    attempt = QuizAttempt(
                        user_id=student.id,
                        quiz_id=quiz.id,
                        score=score
                    )
                    db.session.add(attempt)
                    quiz_attempt_count += 1
            
            # 30% học viên nộp bài tập và đã được chấm điểm
            if random.random() > 0.7:
                existing_sub = Submission.query.filter_by(user_id=student.id, assignment_id=assignment.id).first()
                if not existing_sub:
                    sub = Submission(
                        user_id=student.id,
                        assignment_id=assignment.id,
                        text_content="Em nộp link github chứa bài tập landing page ạ: https://github.com/...",
                        status="graded",
                        score=random.randint(70, 100),
                        feedback="Làm rất tốt! Layout đẹp nhưng chú ý thêm responsive nhé."
                    )
                    db.session.add(sub)
                    submission_count += 1

        db.session.commit()
        print(f"Đã giả lập {quiz_attempt_count} lượt làm Quiz và {submission_count} lượt nộp Bài tập.")
        print("Mở '/teacher/dashboard' > Khóa học mẫu > Chọn 'Sổ điểm' để xem!")

if __name__ == "__main__":
    seed_content()

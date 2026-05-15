import csv
from datetime import timezone
from sqlalchemy import func
from e16_app import create_app
from e16_app.extensions import db
from e16_app.models import User, Course, Enrollment, LearningLog, QuizAttempt, Lesson

def run_export():
    app = create_app()
    with app.app_context():
        print("Đang xuất dữ liệu cho Looker Studio...")
        
        # Lấy tất cả enrollments
        enrollments = db.session.query(Enrollment).all()
        
        # Mở file CSV để ghi
        with open('datastudio_export.csv', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            # Header theo yêu cầu của Data Studio
            writer.writerow([
                'user_id', 'course_title', 'enroll_date', 
                'is_enrolled', 'is_started', 'is_completed', 
                'avg_quiz_score', 'tốc độ học'
            ])
            
            count_started = 0
            count_completed = 0
            total_rows = 0
            
            for e in enrollments:
                course = db.session.get(Course, e.course_id)
                if not course:
                    continue
                
                total_rows += 1
                # is_enrolled mặc định là 1 cho mỗi record
                is_enrolled = 1
                
                # is_completed: nếu status là 'completed'
                is_completed = 1 if e.status == 'completed' else 0
                if is_completed: count_completed += 1
                
                # is_started: kiểm tra xem user đã có learning_log nào cho khóa này chưa
                lesson_ids = [l.id for l in db.session.query(Lesson.id).filter_by(course_id=e.course_id).all()]
                
                has_logs = False
                if lesson_ids:
                    has_logs = db.session.query(LearningLog).filter(
                        LearningLog.user_id == e.user_id,
                        LearningLog.lesson_id.in_(lesson_ids)
                    ).first() is not None
                    
                is_started = 1 if (has_logs or is_completed == 1) else 0
                if is_started: count_started += 1
                
                # avg_quiz_score: điểm trung bình các bài quiz của user trong khóa này
                sql_query = """
                    SELECT AVG(qa.score) 
                    FROM quiz_attempts qa
                    JOIN quizzes q ON qa.quiz_id = q.id
                    WHERE qa.user_id = :uid AND q.course_id = :cid
                """
                result = db.session.execute(db.text(sql_query), {"uid": e.user_id, "cid": e.course_id}).scalar()
                avg_quiz_score = round(float(result), 2) if result else 0
                
                # tốc độ học
                toc_do_hoc = "Đang học"
                if is_completed == 1:
                    toc_do_hoc = "Bình thường"
                
                enroll_date = e.enrolled_at.strftime("%Y-%m-%d")
                
                writer.writerow([
                    e.user_id,
                    course.title,
                    enroll_date,
                    is_enrolled,
                    is_started,
                    is_completed,
                    avg_quiz_score,
                    toc_do_hoc
                ])
                
        print(f"Đã xuất xong file datastudio_export.csv!")
        print(f"--- THỐNG KÊ XUẤT FILE ---")
        print(f"Tổng số dòng: {total_rows}")
        print(f"Số lượng Đã Bắt đầu: {count_started}")
        print(f"Số lượng Đã Tốt nghiệp: {count_completed}")
        print(f"--------------------------")

if __name__ == "__main__":
    run_export()

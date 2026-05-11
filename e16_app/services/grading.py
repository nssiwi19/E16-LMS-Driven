from ..extensions import db
from ..models import Quiz, QuizAttempt, QuizAnswer, Question, Choice, Submission
from datetime import datetime

class GradingService:
    @staticmethod
    def grade_quiz_attempt(user_id, quiz_id, answers_data):
        """
        Grades a quiz attempt and saves it to the database.
        answers_data: dict of {question_id: choice_id}
        """
        quiz = db.session.get(Quiz, quiz_id)
        if not quiz:
            return None
            
        questions = db.session.query(Question).filter_by(quiz_id=quiz_id).all()
        total_questions = len(questions)
        correct_count = 0
        
        attempt = QuizAttempt(user_id=user_id, quiz_id=quiz_id)
        db.session.add(attempt)
        db.session.flush() # Get attempt ID
        
        for q in questions:
            user_choice_id = answers_data.get(str(q.id))
            is_correct = False
            
            if user_choice_id:
                correct_choice = db.session.query(Choice).filter_by(question_id=q.id, is_correct=True).first()
                if correct_choice and str(correct_choice.id) == str(user_choice_id):
                    correct_count += 1
                    is_correct = True
                
                answer = QuizAnswer(
                    attempt_id=attempt.id,
                    question_id=q.id,
                    choice_id=user_choice_id
                )
                db.session.add(answer)
        
        score = (correct_count / total_questions * 100) if total_questions > 0 else 0
        attempt.score = score
        attempt.completed_at = datetime.utcnow()
        db.session.commit()
        
        return attempt

    @staticmethod
    def grade_assignment_submission(submission_id, score, feedback, teacher_id):
        """
        Updates an assignment submission with a grade and feedback.
        """
        sub = db.session.get(Submission, submission_id)
        if not sub:
            return False
            
        sub.score = score
        sub.feedback = feedback
        sub.graded_at = datetime.utcnow()
        sub.graded_by = teacher_id
        db.session.commit()
        return True

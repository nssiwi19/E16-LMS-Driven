from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from sqlalchemy import func

from ..auth_utils import role_required
from ..extensions import db
from ..models import User, Course, Enrollment, LearningLog

bp = Blueprint("analytics", __name__, url_prefix="/analytics")


@bp.route("/")
@login_required
@role_required("admin")
def dashboard():
    days = int(request.args.get("range", 30))
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Summary Stats
    total_users = db.session.query(User).count()
    total_courses = db.session.query(Course).filter_by(status="published").count()
    total_enrollments = db.session.query(Enrollment).count()
    today_logs = db.session.query(LearningLog).filter(LearningLog.timestamp >= datetime.utcnow().replace(hour=0, minute=0, second=0)).count()
    
    # Growth Data (Line Chart)
    user_growth = db.session.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('count')
    ).filter(User.created_at >= start_date).group_by('date').all()
    
    # Enrollment Trend (Bar Chart)
    enroll_trend = db.session.query(
        func.date(Enrollment.enrolled_at).label('date'),
        func.count(Enrollment.id).label('count')
    ).filter(Enrollment.enrolled_at >= start_date).group_by('date').all()
    
    # Top 5 Courses (Horizontal Bar)
    top_courses = db.session.query(
        Course.title,
        func.count(Enrollment.id).label('enroll_count')
    ).join(Enrollment).group_by(Course.id).order_by(func.count(Enrollment.id).desc()).limit(5).all()
    
    return render_template(
        "admin_analytics.html",
        range=days,
        total_users=total_users,
        total_courses=total_courses,
        total_enrollments=total_enrollments,
        today_logs=today_logs,
        user_growth=user_growth,
        enroll_trend=enroll_trend,
        top_courses=top_courses
    )

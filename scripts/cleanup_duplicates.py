# -*- coding: utf-8 -*-
"""
Cleanup duplicate submissions in the database to prevent migration failures
when applying UniqueConstraint(user_id, assignment_id).
Keeps the submission with the highest score, or the most recent one if ungraded.
"""
import os
import sys
# Inject project root path into sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from e16_app import create_app, db
from e16_app.models import Submission
from sqlalchemy import func

def cleanup():
    app = create_app()
    with app.app_context():
        # Find all duplicates of (user_id, assignment_id)
        duplicates = db.session.query(
            Submission.user_id,
            Submission.assignment_id,
            func.count(Submission.id).label('cnt')
        ).group_by(Submission.user_id, Submission.assignment_id).having(func.count(Submission.id) > 1).all()
        
        if not duplicates:
            print("No duplicate submissions found. Database is already clean.")
            return
            
        print(f"Found {len(duplicates)} duplicate pairs. Starting cleanup...")
        
        removed_count = 0
        for user_id, assignment_id, _ in duplicates:
            # Sort: highest score first, then newest submission date first
            subs = db.session.query(Submission).filter_by(
                user_id=user_id,
                assignment_id=assignment_id
            ).order_by(
                Submission.score.desc(),
                Submission.submitted_at.desc()
            ).all()
            
            # Keep the best one (subs[0]), delete the rest
            to_remove = subs[1:]
            for s in to_remove:
                db.session.delete(s)
                removed_count += 1
                
        db.session.commit()
        print(f"Cleanup finished. Successfully removed {removed_count} duplicate submissions.")

if __name__ == "__main__":
    cleanup()

from e16_app import create_app
from e16_app.extensions import db
from e16_app.models import User

app = create_app()
with app.app_context():
    core_users = {
        "admin@gmail.com": "admin",
        "teacher@gmail.com": "teacher",
        "student@gmail.com": "student"
    }
    
    for email, correct_role in core_users.items():
        user = db.session.query(User).filter_by(email=email).first()
        if user:
            if user.role != correct_role:
                print(f"Fixing {email}: {user.role} -> {correct_role}")
                user.role = correct_role
            else:
                print(f"{email} is already {correct_role}")
        else:
            print(f"{email} not found. Please run seed.")
            
    db.session.commit()
    print("Done.")

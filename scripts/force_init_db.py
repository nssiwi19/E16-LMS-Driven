
import os
from e16_app import create_app, db
from e16_app.models import SystemSetting, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print("Creating all tables...")
    db.create_all()
    
    print("Checking for default settings...")
    if not db.session.query(SystemSetting).filter_by(key="site_name").first():
        db.session.add(SystemSetting(key="site_name", value="E16 LMS", description="Tên hệ thống"))
        print("Added default site_name.")
    
    db.session.commit()
    print("Database initialization complete!")

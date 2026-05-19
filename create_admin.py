import os
from datetime import datetime, timezone
from e16_app import create_app
from e16_app.extensions import db
from e16_app.models import User
from werkzeug.security import generate_password_hash
from supabase import create_client

def get_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if url and key:
        return create_client(url, key)
    return None

app = create_app()

with app.app_context():
    email = "admin@e16.local"
    # Kiểm tra xem admin đã tồn tại chưa
    admin = User.query.filter_by(email=email).first()
    
    if not admin:
        admin = User(
            email=email,
            password_hash=generate_password_hash("admine16"),
            role="admin",
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print(f"✅ Đã tạo thành công tài khoản Admin trong SQLite Local!")
    else:
        admin.password_hash = generate_password_hash("admine16")
        admin.role = "admin"
        admin.is_active = True
        db.session.commit()
        print(f"✅ Tài khoản Admin đã tồn tại. Đã reset lại mật khẩu!")

    print(f"📧 Email: {email}")
    print(f"🔑 Mật khẩu: admine16")

    # Đồng bộ lên Supabase
    supabase = get_supabase()
    if supabase:
        print("Đang đồng bộ tài khoản Admin lên Supabase...")
        try:
            sb_admin = {
                "id": admin.id,
                "email": admin.email,
                "password_hash": admin.password_hash,
                "phone": admin.phone,
                "role": admin.role,
                "is_active": admin.is_active,
                "login_count": admin.login_count or 0,
                "created_at": admin.created_at.isoformat() if admin.created_at else datetime.now(timezone.utc).isoformat()
            }
            try:
                supabase.table("users").upsert([sb_admin]).execute()
            except Exception as e:
                err_msg = str(e)
                if "is_active" in err_msg or "phone" in err_msg:
                    print("⚠️ Supabase schema mismatch detected. Retrying with basic fields...")
                    if "is_active" in err_msg:
                        sb_admin.pop("is_active", None)
                    if "phone" in err_msg:
                        sb_admin.pop("phone", None)
                    supabase.table("users").upsert([sb_admin]).execute()
                else:
                    raise e
            print("✅ Đã đồng bộ lên Supabase thành công!")
        except Exception as e:
            print(f"❌ Lỗi khi đồng bộ Supabase: {e}")
    else:
        print("⚠️ Không tìm thấy cấu hình Supabase (SUPABASE_URL / SUPABASE_KEY) trong file .env")

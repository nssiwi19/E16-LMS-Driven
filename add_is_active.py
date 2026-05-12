from e16_app import create_app
from e16_app.extensions import db

app = create_app()

def run_update():
    with app.app_context():
        try:
            db.session.execute(db.text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1"))
            db.session.commit()
            print("Đã thêm cột 'is_active' vào bảng users. Mặc định là TRUE.")
        except Exception as e:
            db.session.rollback()
            print("Cột 'is_active' đã tồn tại hoặc có lỗi:", e)

if __name__ == "__main__":
    run_update()

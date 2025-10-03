from datetime import datetime
from app.extensions import db

class Owner(db.Model):
    __tablename__ = "owners"

    id = db.Column(db.Integer, primary_key=True)
    full_name_th = db.Column(db.String(120), nullable=False)
    full_name_en = db.Column(db.String(120))
    citizen_id = db.Column(db.String(13), unique=True, nullable=False)
    occupancy_notice_pdf = db.Column(db.String(255))
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    
    # --- vvv ส่วนที่แก้ไข vvv ---
    is_active = db.Column(db.Boolean, default=False, nullable=False)
    approval_status = db.Column(db.String(16), default="pending", nullable=False) # pending, approved, rejected
    # --- ^^^ สิ้นสุดส่วนที่แก้ไข ^^^ ---

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Owner id={self.id} email={self.email!r}>"

class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(120))
    role = db.Column(db.String(20), default="admin")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)

    def __repr__(self) -> str:
        return f"<Admin id={self.id} username={self.username!r}>"
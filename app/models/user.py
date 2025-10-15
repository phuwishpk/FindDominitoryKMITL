from datetime import datetime, timedelta
from app.extensions import db
from flask import current_app
from itsdangerous import URLSafeTimedSerializer as Serializer

class Owner(db.Model):
    __tablename__ = "owners"

    APPROVAL_PENDING = "pending"
    APPROVAL_APPROVED = "approved"
    APPROVAL_REJECTED = "rejected"

    id = db.Column(db.Integer, primary_key=True)
    full_name_th = db.Column(db.String(120), nullable=False)
    full_name_en = db.Column(db.String(120), nullable=True)
    citizen_id = db.Column(db.String(13), unique=True, nullable=False)
    occupancy_notice_pdf = db.Column(db.String(255))
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    
    is_active = db.Column(db.Boolean, default=False, nullable=False)
    approval_status = db.Column(db.String(16), default=APPROVAL_PENDING, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    deleted_at = db.Column(db.DateTime, nullable=True)

    # --- vvv เพิ่ม 2 ฟังก์ชันนี้เข้ามา vvv ---
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'owner_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expires_sec)
            owner_id = data.get('owner_id')
        except:
            return None
        return Owner.query.get(owner_id)
    # --- ^^^ สิ้นสุดส่วนที่เพิ่ม ^^^ ---

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
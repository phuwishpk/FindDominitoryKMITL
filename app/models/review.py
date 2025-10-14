# app/models/review.py
from app.extensions import db
from datetime import datetime

class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, nullable=True)
    comment = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- vvv ส่วนที่เพิ่มเข้ามา vvv ---
    is_hidden = db.Column(db.Boolean, default=False, nullable=False) # สถานะการซ่อน
    # --- ^^^ สิ้นสุดการแก้ไข ^^^ ---
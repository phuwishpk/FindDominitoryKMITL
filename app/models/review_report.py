# app/models/review_report.py
from app.extensions import db
from datetime import datetime

class ReviewReport(db.Model):
    __tablename__ = "review_reports"

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("owners.id", ondelete="CASCADE"), nullable=False)

    reason = db.Column(db.Text, nullable=False) # เหตุผลที่ขอลบ
    status = db.Column(db.String(16), default=STATUS_PENDING, nullable=False) # สถานะคำร้อง

    reviewed_by_admin_id = db.Column(db.Integer, nullable=True) # ID ของ Admin ที่ตรวจสอบ
    admin_note = db.Column(db.Text, nullable=True) # หมายเหตุจาก Admin

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    # Relationship to easily access the review object
    review = db.relationship("Review", backref="reports")
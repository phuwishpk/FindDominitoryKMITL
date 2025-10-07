import json
from datetime import datetime
from app.extensions import db

class ApprovalRequest(db.Model):
    __tablename__ = "approval_requests"

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("owners.id", ondelete="CASCADE"), nullable=False)
    status = db.Column(db.String(16), default="pending")
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)

    def __repr__(self) -> str:
        return f"<ApprovalRequest id={self.id} prop={self.property_id} status={self.status}>"


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    actor_type = db.Column(db.String(16), nullable=False)
    actor_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(64), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id", ondelete="SET NULL"))
    meta = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} action={self.action}>"

    # --- vvv ส่วนที่แก้ไข vvv ---
    @staticmethod
    def log(actor_type: str, actor_id: int, action: str, property_id: int | None = None, meta: dict | None = None):
        """
        สร้าง Object ของ AuditLog แต่ยังไม่ commit ลงฐานข้อมูล
        เพื่อให้ Service หรือ Route ที่เรียกใช้เป็นผู้จัดการ Transaction เอง
        """
        return AuditLog(
            actor_type=actor_type,
            actor_id=actor_id,
            action=action,
            property_id=property_id,
            meta=json.dumps(meta) if meta else None,
        )
    # --- ^^^ สิ้นสุดส่วนที่แก้ไข ^^^ ---
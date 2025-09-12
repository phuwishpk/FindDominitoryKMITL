from datetime import datetime
from app.extensions import db

class ApprovalRequest(db.Model):
    __tablename__ = "approval_requests"

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("owners.id", ondelete="CASCADE"), nullable=False)

    status = db.Column(db.String(16), default="pending")  # 'pending','approved','rejected'
    note = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)

    def __repr__(self) -> str:
        return f"<ApprovalRequest id={self.id} prop={self.property_id} status={self.status}>"

class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    actor_type = db.Column(db.String(16), nullable=False)  # 'owner' | 'admin'
    actor_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(64), nullable=False)      # e.g., 'submit_property','approve','reject'
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id", ondelete="SET NULL"))
    meta = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} action={self.action}>"

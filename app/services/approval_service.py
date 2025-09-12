from datetime import datetime
from app.extensions import db
from app.models.approval import ApprovalRequest


class ApprovalService:
    def submit(self, prop, owner_id: int):
        if prop.workflow_status not in ("draft", "rejected"):
            raise ValueError("Only draft/rejected can be submitted")
            prop.workflow_status = "pending"
            req = ApprovalRequest(property_id=prop.id, owner_id=owner_id)
            db.session.add(req)
            db.session.commit()
            return req


    def approve(self, prop, admin_id: int, note: str | None = None):
        if prop.workflow_status != "pending":
         raise ValueError("Only pending can be approved")    
        prop.workflow_status = "approved"
        prop.approved_at = datetime.utcnow()
        ApprovalRequest.query.filter_by(property_id=prop.id, status="pending").update({
        "status": "approved", "reviewed_by_admin_id": admin_id, "reviewed_at": datetime.utcnow()
        })
        db.session.commit()


    def reject(self, prop, admin_id: int, reason: str):
        if prop.workflow_status != "pending":
         raise ValueError("Only pending can be rejected")
        prop.workflow_status = "rejected"
        ApprovalRequest.query.filter_by(property_id=prop.id, status="pending").update({
        "status": "rejected", "reason": reason, "reviewed_by_admin_id": admin_id, "reviewed_at": datetime.utcnow()
        })
        db.session.commit()
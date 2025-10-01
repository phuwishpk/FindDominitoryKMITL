from app.models.property import Property
from app.models.approval import ApprovalRequest, AuditLog
from app.repositories.interfaces.approval_repo import IApprovalRepo
from app.repositories.interfaces.property_repo import IPropertyRepo
from app.extensions import db

class ApprovalService:
    def __init__(self, approval_repo: IApprovalRepo, property_repo: IPropertyRepo):
        self.approval_repo = approval_repo
        self.property_repo = property_repo

    def submit_property(self, property_id: int, owner_id: int) -> None:
        """
        Owner ส่งคำขออนุมัติสำหรับ Property
        """
        prop = self.property_repo.get(property_id)
        if not prop or prop.owner_id != owner_id:
            raise ValueError("Property not found or not owned by user")
        
        # 💡 Logic การเปลี่ยนสถานะและสร้าง Approval Request
        prop.workflow_status = "submitted"
        approval_request = ApprovalRequest(property_id=property_id, owner_id=owner_id, status="pending")
        
        self.approval_repo.add_request(approval_request)
        self.property_repo.save(prop)

        # 💡 Logic การบันทึก AuditLog
        AuditLog.log(
            actor_type="owner",
            actor_id=owner_id,
            action="submit_approval",
            property_id=property_id,
        )

    def approve_property(self, admin_id: int, prop_id: int, note: str | None = None) -> None:
        """
        Admin อนุมัติ Property
        """
        prop = self.property_repo.get(prop_id)
        if not prop:
            raise ValueError("Property not found")

        prop.workflow_status = "approved"
        
        approval_request = self.approval_repo.get_pending_request(prop_id)
        if approval_request:
            approval_request.status = "approved"
            approval_request.note = note
            self.approval_repo.update_request(approval_request)

        self.property_repo.save(prop)
        
        AuditLog.log(
            actor_type="admin",
            actor_id=admin_id,
            action="approve_property",
            property_id=prop_id,
            meta={"note": note},
        )

    def reject_property(self, admin_id: int, prop_id: int, note: str | None = None) -> None:
        """
        Admin ปฏิเสธ Property
        """
        prop = self.property_repo.get(prop_id)
        if not prop:
            raise ValueError("Property not found")

        prop.workflow_status = "rejected"

        approval_request = self.approval_repo.get_pending_request(prop_id)
        if approval_request:
            approval_request.status = "rejected"
            approval_request.note = note
            self.approval_repo.update_request(approval_request)
        
        self.property_repo.save(prop)

        AuditLog.log(
            actor_type="admin",
            actor_id=admin_id,
            action="reject_property",
            property_id=prop_id,
            meta={"note": note},
        )

    def get_audit_logs(self, page: int = 1, per_page: int = 20) -> dict:
        """
        ดึงข้อมูลบันทึกกิจกรรม (AuditLog) แบบแบ่งหน้า
        """
        logs = self.approval_repo.list_logs(page=page, per_page=per_page)
        return {
            "items": logs.items,
            "total": logs.total,
            "page": logs.page,
            "per_page": logs.per_page,
            "pages": logs.pages,
        }
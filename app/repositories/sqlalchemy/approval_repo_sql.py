from app.models.property import Property
from app.models.approval import ApprovalRequest, AuditLog
from app.extensions import db

class SqlApprovalRepo:
    """
    Repository สำหรับจัดการ ApprovalRequest และ AuditLog
    """
    def get_pending_properties(self):
        """
        ดึงรายการ Properties ทั้งหมดที่อยู่ในสถานะ 'submitted' (รออนุมัติ)
        """
        # ใช้ .all() เพื่อให้ได้ list ของ Property objects
        return Property.query.filter_by(workflow_status='submitted').all()

    def get_pending_request(self, property_id: int) -> ApprovalRequest | None:
        """
        ดึง ApprovalRequest ล่าสุดที่มีสถานะเป็น 'pending' สำหรับ Property นั้นๆ
        """
        return ApprovalRequest.query.filter_by(
            property_id=property_id,
            status='pending'
        ).order_by(ApprovalRequest.created_at.desc()).first()

    def add_request(self, req: ApprovalRequest) -> ApprovalRequest:
        """
        เพิ่ม ApprovalRequest ใหม่ลงในฐานข้อมูล
        """
        db.session.add(req)
        db.session.commit()
        return req

    def update_request(self, req: ApprovalRequest):
        """
        บันทึกการเปลี่ยนแปลงของ ApprovalRequest
        """
        db.session.commit()
        
    def list_logs(self, page: int = 1, per_page: int = 20):
        """
        ดึง AuditLog ทั้งหมดพร้อมการแบ่งหน้า (Pagination)
        """
        # ใช้ .paginate() ของ SQLAlchemy 2.0
        return db.paginate(
            AuditLog.query.order_by(AuditLog.created_at.desc()), 
            page=page, per_page=per_page, error_out=False
        )
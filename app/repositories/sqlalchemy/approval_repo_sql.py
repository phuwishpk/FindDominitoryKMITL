from app.models.property import Property
from app.models.approval import ApprovalRequest, AuditLog
from app.extensions import db
from sqlalchemy import or_

class SqlApprovalRepo:
    
    def get_pending_properties(self, search_query: str = None):
        """
        ดึงรายการ Properties ทั้งหมดที่อยู่ในสถานะ 'submitted' (รออนุมัติ)
        พร้อมความสามารถในการค้นหา และเรียงตาม ID น้อยไปมาก
        """
        query = Property.query.filter_by(workflow_status='submitted')
        
        if search_query:
            like_query = f"%{search_query}%"
            query = query.filter(
                or_(
                    Property.dorm_name.ilike(like_query),
                    Property.owner_id.ilike(like_query) 
                )
            )
            
        return query.order_by(Property.id.asc()).all()

    def get_pending_request(self, property_id: int) -> ApprovalRequest | None:
        return ApprovalRequest.query.filter_by(
            property_id=property_id,
            status='pending'
        ).order_by(ApprovalRequest.created_at.desc()).first()

    def add_request(self, req: ApprovalRequest) -> ApprovalRequest:
        db.session.add(req)
        db.session.commit()
        return req

    def update_request(self, req: ApprovalRequest):
        db.session.commit()
        
    def list_logs(self, page: int = 1, per_page: int = 20):
        """
        ดึง AuditLog ทั้งหมดพร้อมการแบ่งหน้า (Pagination) และเรียงตาม ID น้อยไปมาก
        """
        # --- vvv ส่วนที่แก้ไข vvv ---
        return db.paginate(
            AuditLog.query.order_by(AuditLog.id.asc()), # เปลี่ยนเป็นเรียงตาม ID น้อยไปมาก
            page=page, per_page=per_page, error_out=False
        )
        # --- ^^^ สิ้นสุดส่วนที่แก้ไข ^^^ ---
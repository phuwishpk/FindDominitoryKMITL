from app.extensions import db
from sqlalchemy import or_, desc # นำเข้าเฉพาะที่จำเป็น

class SqlApprovalRepo:
    
    def get_pending_properties(self, search_query: str = None):
        from app.models.property import Property # FIX: นำเข้าภายในฟังก์ชัน
        from app.models.user import Owner # FIX: นำเข้า Owner เพื่อ Join
        """
        ดึงรายการ Properties ทั้งหมดที่อยู่ในสถานะ 'submitted' (รออนุมัติ)
        พร้อมความสามารถในการค้นหา และเรียงตาม ID น้อยไปมาก
        """
        query = Property.query.filter_by(workflow_status='submitted')
        
        if search_query:
            like_query = f"%{search_query}%"
            # ใช้ Join เพื่อค้นหาจากชื่อ Owner หรือชื่อหอพัก
            query = query.join(Property.owner).filter(
                or_(
                    Property.dorm_name.ilike(like_query),
                    Owner.full_name_th.ilike(like_query) 
                )
            )
            
        return query.order_by(Property.id.asc()).all()

    def get_pending_request(self, property_id: int):
        from app.models.approval import ApprovalRequest # FIX: นำเข้าภายในฟังก์ชัน
        return ApprovalRequest.query.filter_by(
            property_id=property_id,
            status='pending'
        ).order_by(desc(ApprovalRequest.created_at)).first()

    def add_request(self, req):
        db.session.add(req)
        db.session.commit()
        return req

    def update_request(self, req):
        db.session.commit()
        
    def list_logs(self, page: int = 1, per_page: int = 20):
        from app.models.approval import AuditLog # FIX: นำเข้าภายในฟังก์ชัน
        """
        ดึง AuditLog ทั้งหมดพร้อมการแบ่งหน้า (Pagination)
        """
        return db.paginate(
            AuditLog.query.order_by(AuditLog.created_at.desc()), 
            page=page, per_page=per_page, error_out=False
        )
        
    def permanently_delete_owner(self, owner):
        # NOTE: เมธอดนี้อาจจำเป็นสำหรับ OwnerRepo แต่ยังคงไว้ที่นี่ถ้าโค้ดอื่นเรียกใช้
        pass 

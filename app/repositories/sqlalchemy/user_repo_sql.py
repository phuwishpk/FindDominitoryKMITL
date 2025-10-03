from app.extensions import db
from app.models.user import Owner, Admin
from sqlalchemy import or_

class SqlUserRepo:
    def add_owner(self, owner: Owner) -> Owner:
        db.session.add(owner); db.session.commit()
        return owner

    def get_owner_by_email(self, email: str):
        return Owner.query.filter_by(email=email).first()

    def get_admin_by_username(self, username: str):
        return Admin.query.filter_by(username=username).first()

    # ส่วนที่เพิ่มเข้ามาใหม่
    def list_all_owners_paginated(self, search_query=None, page=1, per_page=15):
        """
        ดึงรายการ Owners ทั้งหมด พร้อมค้นหาและแบ่งหน้า
        (Fetches all Owners with search and pagination)
        """
        q = Owner.query

        if search_query:
            like_filter = f"%{search_query}%"
            q = q.filter(
                or_(
                    Owner.full_name_th.ilike(like_filter),
                    Owner.email.ilike(like_filter)
                )
            )

        return db.paginate(
            q.order_by(Owner.created_at.desc()),
            page=page, per_page=per_page, error_out=False
        )
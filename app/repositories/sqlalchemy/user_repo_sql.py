from app.extensions import db
from app.models.user import Owner, Admin
from sqlalchemy import or_

class SqlUserRepo:
    def add_owner(self, owner: Owner) -> Owner:
        db.session.add(owner)
        db.session.commit()
        return owner

    def get_owner_by_email(self, email: str):
        return Owner.query.filter_by(email=email).first()

    def get_admin_by_username(self, username: str):
        return Admin.query.filter_by(username=username).first()

    def get_owner_by_id(self, owner_id: int):
        return Owner.query.get(owner_id)
        
    def get_pending_owners(self):
        # หน้านี้เรียงตามวันที่สมัครก่อนดีกว่า เพื่อให้คนที่สมัครก่อนได้อนุมัติก่อน
        return Owner.query.filter_by(approval_status='pending').order_by(Owner.created_at.asc()).all()

    def save_owner(self, owner: Owner):
        db.session.commit()

    def list_all_owners_paginated(self, search_query=None, page=1, per_page=15):
        q = Owner.query

        if search_query:
            like_filter = f"%{search_query}%"
            q = q.filter(
                or_(
                    Owner.full_name_th.ilike(like_filter),
                    Owner.email.ilike(like_filter)
                )
            )
            
        # --- vvv ส่วนที่แก้ไข vvv ---
        return db.paginate(
            q.order_by(Owner.id.asc()), # เปลี่ยนเป็นเรียงตาม ID น้อยไปมาก
            page=page, per_page=per_page, error_out=False
        )
        # --- ^^^ สิ้นสุดส่วนที่แก้ไข ^^^ ---
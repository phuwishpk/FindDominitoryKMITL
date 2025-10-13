from app.extensions import db
from app.models.user import Owner, Admin
from sqlalchemy import or_, func
from datetime import datetime

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
        return Owner.query.filter_by(approval_status=Owner.APPROVAL_PENDING).order_by(Owner.created_at.asc()).all()

    def save_owner(self, owner: Owner):
        db.session.commit()

    def get_deleted_owners_paginated(self, page=1, per_page=15):
        q = Owner.query.filter(Owner.deleted_at.isnot(None))
        return db.paginate(q.order_by(Owner.deleted_at.desc()), page=page, per_page=per_page, error_out=False)
    
    def permanently_delete_owner(self, owner: Owner):
        db.session.delete(owner)
        db.session.commit()

    def list_all_owners_paginated(self, search_query=None, page=1, per_page=15):
        q = Owner.query.filter(Owner.deleted_at.is_(None))

        if search_query:
            like_filter = f"%{search_query}%"
            q = q.filter(
                or_(
                    Owner.full_name_th.ilike(like_filter),
                    Owner.email.ilike(like_filter)
                )
            )
            
        return db.paginate(
            q.order_by(Owner.id.asc()),
            page=page, per_page=per_page, error_out=False
        )

    def count_active_owners(self) -> int:
        return db.session.query(Owner).filter(Owner.deleted_at.is_(None)).count()

    def count_owners_by_month(self, date_obj: datetime) -> int:
        return db.session.query(Owner).filter(
            func.strftime('%Y-%m', Owner.created_at) == date_obj.strftime("%Y-%m")
        ).count()
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from datetime import datetime

from app.extensions import db
from sqlalchemy import or_

if TYPE_CHECKING:
    # ใช้เฉพาะตอน type-check; ไม่รันตอนจริง (กันวงจรอิมพอร์ต)
    from app.models.user import Owner, Admin


class SqlUserRepo:
    def add_owner(self, owner: "Owner") -> "Owner":
        db.session.add(owner)
        db.session.commit()
        return owner

    def save_owner(self, owner: "Owner"):
        """Commits changes to an existing Owner object (e.g., updating PDF path)."""
        db.session.commit()

    def permanently_delete_owner(self, owner: "Owner"):
        db.session.delete(owner)
        db.session.commit()

    def get_owner_by_email(self, email: str) -> Optional["Owner"]:
        from app.models.user import Owner
        return Owner.query.filter_by(email=email).first()

    def get_admin_by_username(self, username: str) -> Optional["Admin"]:
        from app.models.user import Admin
        return Admin.query.filter_by(username=username).first()

    def get_owner_by_id(self, owner_id: int) -> Optional["Owner"]:
        from app.models.user import Owner
        # แนะนำให้ใช้ session.get แทน Query.get (SQLAlchemy 2.x)
        return db.session.get(Owner, owner_id)

    def get_pending_owners(self) -> list["Owner"]:
        from app.models.user import Owner
        return (
            Owner.query
            .filter_by(approval_status=Owner.APPROVAL_PENDING)
            .order_by(Owner.created_at.asc())
            .all()
        )

    def list_all_owners_paginated(self, search_query: Optional[str] = None, page: int = 1, per_page: int = 15):
        from app.models.user import Owner
        q = Owner.query.filter(Owner.deleted_at.is_(None))

        if search_query:
            like_filter = f"%{search_query}%"
            # บาง dialect (เช่น SQLite) LIKE เป็น case-insensitive อยู่แล้ว; ILIKE จะถูกแปลงโดย SA
            q = q.filter(
                or_(
                    Owner.full_name_th.ilike(like_filter),
                    Owner.email.ilike(like_filter),
                )
            )

        return db.paginate(
            q.order_by(Owner.id.asc()),
            page=page,
            per_page=per_page,
            error_out=False,
        )

    def get_deleted_owners_paginated(self, page: int = 1, per_page: int = 15):
        from app.models.user import Owner
        q = Owner.query.filter(Owner.deleted_at.isnot(None))
        return db.paginate(
            q.order_by(Owner.deleted_at.desc()),
            page=page,
            per_page=per_page,
            error_out=False,
        )

    def count_active_owners(self) -> int:
        from app.models.user import Owner
        return (
            db.session.query(Owner)
            .filter(Owner.deleted_at.is_(None))
            .count()
        )

    def count_owners_by_month(self, date_obj: datetime) -> int:
        """นับจำนวนเจ้าของที่สมัครในเดือนเดียวกับ date_obj (พกพาได้ทุกฐานข้อมูล)"""
        from app.models.user import Owner
        # คำนวณช่วงต้นเดือน-ต้นเดือนถัดไป (half-open interval)
        start = date_obj.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1)
        else:
            end = start.replace(month=start.month + 1)

        return (
            db.session.query(Owner)
            .filter(
                Owner.created_at >= start,
                Owner.created_at < end,
                Owner.deleted_at.is_(None),
            )
            .count()
        )
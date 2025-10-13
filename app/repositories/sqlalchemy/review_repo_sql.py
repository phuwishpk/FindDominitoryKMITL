# app/repositories/sqlalchemy/review_repo_sql.py
from __future__ import annotations
from typing import TYPE_CHECKING

from app.extensions import db

if TYPE_CHECKING:
    # ใช้เพื่อ type-check เท่านั้น ไม่ถูก import ตอนรันจริง (กันวงจรอิมพอร์ต)
    from app.models.review import Review


class SqlReviewRepo:
    def add(self, review: "Review") -> "Review":
        """บันทึก Review ลงฐานข้อมูล"""
        db.session.add(review)
        db.session.commit()
        return review

    def get_by_property_id(self, property_id: int) -> list["Review"]:
        """ดึงรีวิวทั้งหมดของหอพัก เรียงจากใหม่ไปเก่า"""
        from app.models.review import Review  # ✅ lazy import
        return (
            Review.query
            .filter_by(property_id=property_id)
            .order_by(Review.created_at.desc())
            .all()
        )

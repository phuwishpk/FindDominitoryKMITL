# app/repositories/sqlalchemy/review_repo_sql.py
from app.models.review import Review
from app.extensions import db

class SqlReviewRepo:
    def add(self, review: Review) -> Review:
        """
        Function 1 (Helper): บันทึก object ของ Review ลงในฐานข้อมูล
        """
        db.session.add(review)
        db.session.commit()
        return review

    # --- vvv นี่คือฟังก์ชัน get() ที่หายไปครับ vvv ---
    def get(self, review_id: int) -> Review | None:
        """
        Function 2 (Helper): ดึงข้อมูลรีวิวจาก ID ที่ระบุ
        """
        return db.session.get(Review, review_id)
    # --- ^^^ สิ้นสุดส่วนที่ขาดหาย ^^^ ---

    def get_by_property_id(self, property_id: int) -> list[Review]:
        """
        Function 3 (Helper): ดึงข้อมูลรีวิวทั้งหมดของหอพักที่ระบุ
        โดยจะกรองรีวิวที่ถูกซ่อนออกไป และเรียงลำดับจากใหม่ที่สุดไปเก่าที่สุด
        """
        return Review.query.filter_by(
            property_id=property_id, 
            is_hidden=False  # กรองรีวิวที่ถูกซ่อนออก
        ).order_by(Review.created_at.desc()).all()
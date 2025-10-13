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

    def get_by_property_id(self, property_id: int) -> list[Review]:
        """
        Function 2 (Helper): ดึงข้อมูลรีวิวทั้งหมดของหอพักที่ระบุ
        เรียงลำดับจากใหม่ที่สุดไปเก่าที่สุด
        """
        return Review.query.filter_by(property_id=property_id).order_by(Review.created_at.desc()).all()
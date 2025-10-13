# app/services/review_service.py
from __future__ import annotations
from typing import TYPE_CHECKING

# db/func ไม่ได้ใช้ในไฟล์นี้ ตัดออกให้สะอาด
# from app.extensions import db
# from sqlalchemy import func

if TYPE_CHECKING:
    # ใช้เพื่อ type-check เท่านั้น ไม่รันตอนจริง
    from app.models.review import Review

class ReviewService:
    def __init__(self, review_repo):
        self.review_repo = review_repo

    def add_review(self, property_id: int, user_id: int, comment: str, rating: int) -> "Review":
        # ✅ lazy import กันวงจรอิมพอร์ต
        from app.models.review import Review

        # ป้องกันค่าผิดปกติ
        if rating is None or not (1 <= int(rating) <= 5):
            raise ValueError("rating must be an integer from 1 to 5")

        new_review = Review(
            property_id=property_id,
            user_id=user_id,
            comment=comment,
            rating=int(rating),
        )
        return self.review_repo.add(new_review)

    def get_reviews_and_average_rating(self, property_id: int) -> dict:
        reviews = self.review_repo.get_by_property_id(property_id)

        if not reviews:
            return {"reviews": [], "average_rating": 0.0}

        total_rating = sum(int(r.rating) for r in reviews)
        average_rating = round(total_rating / len(reviews), 1)
        return {"reviews": reviews, "average_rating": average_rating}

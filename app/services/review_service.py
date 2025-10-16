# app/services/review_service.py

from app.models.review import Review

class ReviewService:
    def __init__(self, review_repo):
        self.review_repo = review_repo

    def add_review(self, property_id: int, user_id: int, comment: str, rating: int) -> Review:
        """
        Function 1: สร้างและบันทึกรีวิวใหม่ลงในฐานข้อมูล
        รับข้อมูลที่จำเป็นสำหรับการสร้างรีวิวใหม่, สร้าง object ของ Review
        และเรียกใช้ repository เพื่อบันทึกลงฐานข้อมูล
        """
        new_review = Review(
            property_id=property_id,
            user_id=user_id,
            comment=comment,
            rating=rating
        )
        return self.review_repo.add(new_review)

    def get_reviews_and_average_rating(self, property_id: int) -> dict:
        """
        Function 2: ดึงข้อมูลรีวิวทั้งหมดและคำนวณคะแนนเฉลี่ยสำหรับหอพัก
        เรียกใช้ repository เพื่อดึงข้อมูลรีวิวทั้งหมด จากนั้นจึงคำนวณคะแนนเฉลี่ย
        """
        reviews = self.review_repo.get_by_property_id(property_id)
        
        if not reviews:
            return {"reviews": [], "average_rating": 0.0}

        total_rating = sum(r.rating for r in reviews)
        average_rating = round(total_rating / len(reviews), 1)

        return {"reviews": reviews, "average_rating": average_rating}

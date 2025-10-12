from app.extensions import db
from app.models.review import Review
from app.repositories.interfaces.review_repo import IReviewRepo

class SqlReviewRepo(IReviewRepo):
    def add(self, review: Review) -> Review:
        db.session.add(review)
        db.session.commit()
        return review

    def get_by_property_id(self, property_id: int) -> list[Review]:
        return Review.query.filter_by(property_id=property_id).order_by(Review.created_at.desc()).all()
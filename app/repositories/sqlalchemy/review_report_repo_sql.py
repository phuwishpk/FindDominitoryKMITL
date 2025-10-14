# app/repositories/sqlalchemy/review_report_repo_sql.py

from app.models.review_report import ReviewReport
from app.models.review import Review
from app.extensions import db
from sqlalchemy.orm import joinedload

class SqlReviewReportRepo:
    def add(self, report: ReviewReport) -> ReviewReport:
        db.session.add(report)
        db.session.commit()
        return report

    def get_by_id(self, report_id: int) -> ReviewReport | None:
        return db.session.get(ReviewReport, report_id)

    def get_pending_reports(self):
        # Preload the review and its associated property to avoid N+1 queries
        return ReviewReport.query.options(
            joinedload(ReviewReport.review).joinedload(Review.property)
        ).filter(
            ReviewReport.status == ReviewReport.STATUS_PENDING
        ).order_by(ReviewReport.created_at.asc()).all()

    def get_reports_by_owner(self, owner_id: int):
        return ReviewReport.query.options(
            joinedload(ReviewReport.review)
        ).filter_by(
            owner_id=owner_id
        ).order_by(ReviewReport.created_at.desc()).all()
    
    def find_existing_report(self, review_id: int) -> ReviewReport | None:
        # Filter instead of filter_by to use '==' for clarity
        return ReviewReport.query.filter(
            ReviewReport.review_id == review_id,
            ReviewReport.status == ReviewReport.STATUS_PENDING
        ).first()

    def save(self, report: ReviewReport):
        db.session.commit()
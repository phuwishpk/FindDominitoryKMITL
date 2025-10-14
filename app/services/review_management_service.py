# app/services/review_management_service.py

from datetime import datetime
from app.models.review import Review
from app.models.review_report import ReviewReport
from app.models.property import Property
from app.models.approval import AuditLog
from app.extensions import db

class ReviewManagementService:
    def __init__(self, review_repo, report_repo, prop_repo):
        self.review_repo = review_repo
        self.report_repo = report_repo
        self.prop_repo = prop_repo

    def can_owner_report_review(self, owner_id: int, review_id: int) -> tuple[bool, str, Review | None]:
        review = self.review_repo.get(review_id)
        if not review:
            return False, "ไม่พบรีวิวนี้", None
        if review.is_hidden:
            return False, "รีวิวนี้ถูกซ่อนอยู่แล้ว", review
        
        prop = self.prop_repo.get(review.property_id)
        if not prop or prop.owner_id != owner_id:
            return False, "คุณไม่มีสิทธิ์จัดการรีวิวนี้", review

        if self.report_repo.find_existing_report(review_id):
            return False, "คุณได้ส่งคำร้องขอลบรีวิวนี้ไปแล้ว", review
            
        return True, "", review

    def request_deletion(self, owner_id: int, review_id: int, reason: str):
        can_report, message, review = self.can_owner_report_review(owner_id, review_id)
        if not can_report:
            raise PermissionError(message)

        report = ReviewReport(
            review_id=review_id,
            property_id=review.property_id,
            owner_id=owner_id,
            reason=reason
        )
        self.report_repo.add(report)
        return report

    def process_report(self, admin_id: int, report_id: int, approve: bool, admin_note: str | None = None):
        report = self.report_repo.get_by_id(report_id)
        if not report or report.status != ReviewReport.STATUS_PENDING:
            raise ValueError("ไม่พบคำร้องขอ หรือคำร้องนี้ถูกจัดการไปแล้ว")

        report.reviewed_by_admin_id = admin_id
        report.reviewed_at = datetime.utcnow()
        report.admin_note = admin_note
        
        log_meta = {"report_id": report.id, "review_id": report.review_id}

        if approve:
            report.status = ReviewReport.STATUS_APPROVED
            review = report.review
            review.is_hidden = True
            db.session.add(AuditLog.log("admin", admin_id, "approve_review_deletion", meta=log_meta))
        else:
            report.status = ReviewReport.STATUS_REJECTED
            db.session.add(AuditLog.log("admin", admin_id, "reject_review_deletion", meta=log_meta))
        
        self.report_repo.save(report)
        return report
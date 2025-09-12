from typing import Sequence
from app.models.approval import ApprovalRequest
from app.repositories.interfaces.approval_repo import IApprovalRepo


class SqlApprovalRepo(IApprovalRepo):
    def list_pending(self) -> Sequence[ApprovalRequest]:
        return ApprovalRequest.query.filter_by(status="pending").all()
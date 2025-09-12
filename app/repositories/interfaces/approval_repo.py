from typing import Protocol, Sequence
from app.models.approval import ApprovalRequest


class IApprovalRepo(Protocol):
    def list_pending(self) -> Sequence[ApprovalRequest]: ...
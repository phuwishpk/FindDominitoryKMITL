class ApprovalService:
    def submit(self, prop, owner_id: int):
        prop.workflow_status = "submitted"
        from app.extensions import db
        db.session.commit()

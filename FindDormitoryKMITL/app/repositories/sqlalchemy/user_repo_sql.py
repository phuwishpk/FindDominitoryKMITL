from app.extensions import db
from app.models.user import Owner, Admin

class SqlUserRepo:
    def add_owner(self, owner: Owner) -> Owner:
        db.session.add(owner); db.session.commit()
        return owner

    def get_owner_by_email(self, email: str):
        return Owner.query.filter_by(email=email).first()

    def get_admin_by_username(self, username: str):
        return Admin.query.filter_by(username=username).first()

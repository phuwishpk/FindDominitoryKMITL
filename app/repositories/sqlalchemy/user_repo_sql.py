from typing import Optional
from app.extensions import db
from app.models.user import Owner, Admin
from app.repositories.interfaces.user_repo import IUserRepo


class SqlUserRepo(IUserRepo):
    def get_owner_by_email(self, email: str) -> Optional[Owner]:
        return Owner.query.filter_by(email=email).first()


    def add_owner(self, owner: Owner) -> Owner:
        db.session.add(owner)
        db.session.commit()
        return owner


    def get_admin_by_username(self, username: str) -> Optional[Admin]:
        return Admin.query.filter_by(username=username).first()
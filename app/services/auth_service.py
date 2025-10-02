from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user
from app.models.user import Owner, Admin
from app.extensions import Principal
from app.repositories.interfaces.user_repo import IUserRepo # 💡 นี่คือการ Import ที่ถูกต้อง

class AuthService:
    def __init__(self, user_repo: IUserRepo):
        self.user_repo = user_repo

    def register_owner(self, data: dict) -> Owner:
        owner = Owner(
            full_name_th=data.get("full_name_th"),
            full_name_en=data.get("full_name_en"),
            citizen_id=data.get("citizen_id"),
            email=data.get("email"),
            phone=data.get("phone"),
            password_hash=generate_password_hash(data.get("password"))
        )
        return self.user_repo.add_owner(owner)

    def verify_owner(self, email: str, password: str) -> bool:
        owner = self.user_repo.get_owner_by_email(email)
        return bool(owner and check_password_hash(owner.password_hash, password))

    def login_owner(self, owner: Owner) -> None:
        principal = Principal(f"owner:{owner.id}", "owner", owner.id)
        login_user(principal, remember=True)

    def verify_admin(self, username: str, password: str):
        admin = self.user_repo.get_admin_by_username(username)
        if admin and check_password_hash(admin.password_hash, password):
            return admin
        return None

    def login_admin(self, admin: Admin) -> None:
        principal = Principal(f"admin:{admin.id}", "admin", admin.id)
        login_user(principal, remember=True)

    def logout(self) -> None:
        logout_user()
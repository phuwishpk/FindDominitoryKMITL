import os
import hashlib
from typing import Optional
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from flask_principal import Identity, identity_changed

# Import models and repositories
from ..models import Owner, Admin
from ..repositories import OwnerRepository, AdminRepository


class AuthService:
    """
    Service class for handling authentication logic for both Owners and Admins.
    """

    def __init__(self, owner_repo: OwnerRepository, admin_repo: AdminRepository):
        """
        Constructor with Dependency Injection of Repositories.
        """
        self.owner_repo = owner_repo
        self.admin_repo = admin_repo

    def register_owner(self, data: dict) -> Owner:
        """
        Register a new Owner.
        - Validate data (check duplicate email)
        - Hash password
        - Store PDF paths if any
        - Save to database
        """
        email = data.get('email')
        if self.owner_repo.find_by_email(email):
            raise ValueError(f"Owner with email {email} already exists.")

        password = data.get('password')
        if not password:
            raise ValueError("Password is required.")

        hashed_password = generate_password_hash(password)

        new_owner = Owner(
            email=email,
            password_hash=hashed_password,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            business_license_pdf_path=data.get('business_license_pdf_path'),
            id_card_pdf_path=data.get('id_card_pdf_path')
        )

        self.owner_repo.add(new_owner)
        return new_owner

    def verify_owner(self, email: str, password: str) -> Optional[Owner]:
        """
        Verify an Owner's email and password.
        """
        owner = self.owner_repo.find_by_email(email)
        if owner and check_password_hash(owner.password_hash, password):
            return owner
        return None

    def login_owner(self, owner: Owner) -> None:
        """
        Log in an Owner using Flask-Login and set identity for Flask-Principal.
        """
        login_user(owner)
        identity_changed.send(current_app._get_current_object(), identity=Identity(owner.id, 'owner'))

    def verify_admin(self, username: str, password: str) -> Optional[Admin]:
        """
        Verify an Admin's username and password.
        """
        admin = self.admin_repo.find_by_username(username)
        if admin and check_password_hash(admin.password_hash, password):
            return admin
        return None

    def login_admin(self, admin: Admin) -> None:
        """
        Log in an Admin using Flask-Login and set identity for Flask-Principal.
        """
        login_user(admin)
        identity_changed.send(current_app._get_current_object(), identity=Identity(admin.id, 'admin'))

    def logout(self) -> None:
        """
        Log out the current user and clear their identity.
        """
        logout_user()
        identity_changed.send(current_app._get_current_object(), identity=Identity(None, None))

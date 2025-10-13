# File: app/repositories/interfaces/user_repo.py

# ⬇️ [Python Standard Lib]
from abc import ABC, abstractmethod

class IUserRepo(ABC):
    @abstractmethod
    def add_owner(self, owner): ...
    @abstractmethod
    def save_owner(self, owner): ... # 🛠️ [app/repositories/interfaces/user_repo.py] เพิ่มเมธอดนี้สำหรับอัปเดต Owner (จำเป็นสำหรับ register_owner ที่มีการจัดการ PDF)
    @abstractmethod
    def get_owner_by_email(self, email: str): ...
    @abstractmethod
    def get_admin_by_username(self, username: str): ...
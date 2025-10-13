from abc import ABC, abstractmethod

class IUserRepo(ABC):
    @abstractmethod
    def add_owner(self, owner): ...
    @abstractmethod
    def save_owner(self, owner): ... # เพิ่มเมธอดนี้
    @abstractmethod
    def get_owner_by_email(self, email: str): ...
    @abstractmethod
    def get_admin_by_username(self, username: str): ...
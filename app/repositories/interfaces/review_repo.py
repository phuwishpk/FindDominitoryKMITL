from abc import ABC, abstractmethod
from app.models.review import Review

class IReviewRepo(ABC):
    @abstractmethod
    def add(self, review: Review) -> Review: ...
    
    @abstractmethod
    def get_by_property_id(self, property_id: int) -> list[Review]: ...
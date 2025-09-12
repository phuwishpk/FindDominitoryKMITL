from typing import Any, Dict
from app.repositories.interfaces.property_repo import IPropertyRepo


class SearchService:
    def __init__(self, repo: IPropertyRepo):
        self.repo = repo


    def search(self, filters: Dict[str, Any], page: int = 1, per_page: int = 12):
        # TODO: apply filters and pagination using repo
        items = self.repo.list_approved(**filters)
        return {"items": items, "page": page, "per_page": per_page, "total": len(items)}
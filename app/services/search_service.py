from math import ceil

class SearchService:
    def __init__(self, property_repo):
        self.repo = property_repo

    def search(self, filters: dict, page: int = 1, per_page: int = 12):
        q = self.repo.list_approved(**(filters or {}))
        total = q.count()
        items = q.offset((page-1)*per_page).limit(per_page).all()
        pages = ceil(total / per_page) if per_page else 1
        return {"items": items, "page": page, "per_page": per_page, "total": total, "pages": pages}

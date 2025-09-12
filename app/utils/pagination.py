from math import ceil


def paginate(total: int, page: int, per_page: int):
    pages = max(1, ceil(total / per_page))
    return {"page": page, "per_page": per_page, "pages": pages}
from math import ceil

class SearchService:
    def __init__(self, property_repo):
        self.repo = property_repo

    def search(self, filters: dict, page: int = 1, per_page: int = 12):
        """
        รวมตรรกะค้นหา: แปลง query string → filters ที่ repo รองรับ,
        เรียก repo, จัดหน้า (pagination), คืน dict ข้อมูลสำหรับแสดงผล
        """
        # เรียกใช้ repository พร้อม filters
        query = self.repo.list_approved(**(filters or {}))

        # นับจำนวนรายการทั้งหมดก่อนแบ่งหน้า
        total = query.count()

        # แบ่งหน้าข้อมูล
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        pages = ceil(total / per_page) if per_page > 0 else 1

        return {
            "items": items,
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages,
        }
from math import ceil
from app.repositories.sqlalchemy.property_repo_sql import SqlPropertyRepo

class SearchService:
    def __init__(self, property_repo: SqlPropertyRepo):
        self.repo = property_repo

    def search(self, search_args: dict, page: int = 1, per_page: int = 12):
        """
        รับค่าจากฟอร์มค้นหาทั้งหมด, สร้างเงื่อนไข, และส่งต่อไปยัง Repository
        """
        filters = {}
        q = search_args.get('q', '').strip()
        if q:
            filters['q'] = q

        road = search_args.get('road', '').strip()
        if road:
            filters['road'] = road

        soi = search_args.get('soi', '').strip()
        if soi:
            filters['soi'] = soi
            
        try:
            min_price = search_args.get('min_price')
            if min_price:
                filters['min_price'] = int(min_price)
        except (ValueError, TypeError):
            pass

        try:
            max_price = search_args.get('max_price')
            if max_price:
                filters['max_price'] = int(max_price)
        except (ValueError, TypeError):
            pass

        room_type = search_args.get('room_type')
        if room_type == 'other':
            filters['room_type'] = search_args.get('other_room_type', '').strip()
        elif room_type:
            filters['room_type'] = room_type
        
        amenities = search_args.getlist('amenities')
        if amenities:
            filters['amenities'] = amenities

        query = self.repo.list_approved_and_ranked(**filters)
        
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        pages = ceil(total / per_page) if per_page else 1
        
        return {
            "items": items,
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages,
            "search_args": search_args
        }
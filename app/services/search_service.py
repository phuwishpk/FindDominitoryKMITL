from math import ceil
from app.repositories.sqlalchemy.property_repo_sql import SqlPropertyRepo

class SearchService:
    def __init__(self, property_repo: SqlPropertyRepo):
        self.repo = property_repo

    def _get_string_arg(self, search_args: dict, key: str) -> str:
        """Safely retrieves and strips a string argument, handling None/missing cases."""
        value = search_args.get(key)
        if value is None:
            return ""
        try:
            return str(value).strip()
        except AttributeError:
            return ""

    def _get_int_arg(self, search_args: dict, key: str) -> int | None:
        """Safely retrieves and casts an argument to integer."""
        value = search_args.get(key)
        if value is None or value == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def search(self, search_args: dict, page: int = 1, per_page: int = 12):
        """
        รับค่าจากฟอร์มค้นหาทั้งหมด, สร้างเงื่อนไข, และส่งต่อไปยัง Repository
        """
        if not search_args:
            search_args = {}
            
        filters = {}
        
        # Safely extract text search terms
        q = self._get_string_arg(search_args, 'q')
        if q:
            filters['q'] = q

        # Safely extract address components (assuming these fields exist on property model and repo handles them)
        road = self._get_string_arg(search_args, 'road')
        if road:
            filters['road'] = road

        soi = self._get_string_arg(search_args, 'soi')
        if soi:
            filters['soi'] = soi
            
        # Safely extract price ranges
        min_price = self._get_int_arg(search_args, 'min_price')
        if min_price is not None:
            filters['min_price'] = min_price

        max_price = self._get_int_arg(search_args, 'max_price')
        if max_price is not None:
            filters['max_price'] = max_price

        # Safely extract room type
        room_type = self._get_string_arg(search_args, 'room_type')
        if room_type == 'other':
            filters['room_type'] = self._get_string_arg(search_args, 'other_room_type')
        elif room_type:
            filters['room_type'] = room_type
        
        # Safely extract amenities list
        amenities = search_args.get('amenities', [])
        if amenities and isinstance(amenities, list):
            filters['amenities'] = amenities

        # FIXED: Changed list_approved_and_ranked to the correct list_approved method.
        query = self.repo.list_approved(**filters)
        
        total = query.count()
        safe_page = max(1, page)
        
        items = query.offset((safe_page - 1) * per_page).limit(per_page).all()
        pages = ceil(total / per_page) if per_page else 1
        
        return {
            "items": items,
            "page": safe_page,
            "per_page": per_page,
            "total": total,
            "pages": pages,
            "search_args": search_args
        }

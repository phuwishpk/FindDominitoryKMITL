from sqlalchemy import or_, func
from app.models.property import Property, Amenity, PropertyAmenity

class SqlPropertyRepo:
    def get(self, prop_id: int):
        # ดึงข้อมูล Property ที่มีสถานะ approved เท่านั้น
        return Property.query.filter_by(id=prop_id, workflow_status="approved").first()

    def add(self, prop: Property) -> Property:
        from app.extensions import db
        db.session.add(prop)
        db.session.commit()
        return prop

    def save(self, prop: Property):
        from app.extensions import db
        db.session.commit()

    def list_approved(self, **filters):
        """
        คืน SQLAlchemy Query ของประกาศที่ workflow_status='approved'
        พร้อมฟิลเตอร์ q, price_min/max, room_type, availability, amenities AND, ordering
        — ไม่ execute เพื่อให้ service คุม paginate เอง
        """
        q = Property.query.filter(Property.workflow_status == "approved")

        # 1. Filter by text search (q)
        q_text = filters.get('q')
        if q_text:
            like = f"%{q_text.strip()}%"
            q = q.filter(or_(
                Property.dorm_name.ilike(like),
                Property.facebook_url.ilike(like) # สมมติว่าค้นหาจากชื่อและ FB
            ))

        # 2. Filter by price range
        min_price = filters.get('min_price')
        max_price = filters.get('max_price')
        if min_price is not None:
            q = q.filter(Property.rent_price >= int(min_price))
        if max_price is not None:
            q = q.filter(Property.rent_price <= int(max_price))

        # 3. Filter by room type
        room_type = filters.get('room_type')
        if room_type:
            q = q.filter(Property.room_type == room_type)

        # 4. Filter by availability
        availability = filters.get('availability')
        if availability in {"vacant", "occupied"}:
            q = q.filter(Property.availability_status == availability)

        # 5. Filter by amenities (ต้องมีครบทุกอย่างที่เลือก - AND logic)
        codes = filters.get('amenities')
        if codes:
            codes_list = [c.strip() for c in codes.split(',') if c.strip()]
            if codes_list:
                q = (
                    q.join(PropertyAmenity)
                     .join(Amenity)
                     .filter(Amenity.code.in_(codes_list))
                     .group_by(Property.id)
                     .having(func.count(func.distinct(Amenity.code)) == len(codes_list))
                )

        # 6. Sorting
        sort = filters.get('sort')
        if sort == 'price_asc':
            q = q.order_by(Property.rent_price.asc())
        elif sort == 'price_desc':
            q = q.order_by(Property.rent_price.desc())
        else: # Default sort
            q = q.order_by(Property.updated_at.desc())

        return q
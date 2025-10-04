from sqlalchemy import or_, func
from app.models.property import Property, Amenity, PropertyAmenity

class SqlPropertyRepo:
    def get(self, prop_id: int):
        return Property.query.get(prop_id)

    def add(self, prop: Property) -> Property:
        from app.extensions import db
        db.session.add(prop)
        db.session.commit()
        return prop

    def save(self, prop: Property):
        from app.extensions import db
        db.session.commit()

    # --- vvv ส่วนที่เพิ่มเข้ามาใหม่ vvv ---
    def delete(self, prop: Property):
        """ลบ Property ออกจากฐานข้อมูล"""
        from app.extensions import db
        db.session.delete(prop)
        db.session.commit()
    # --- ^^^ สิ้นสุดส่วนที่เพิ่ม ^^^ ---

    def list_approved(self, **filters):
        q = Property.query.filter(Property.workflow_status == "approved")
        q_text = (filters or {}).get('q')
        if q_text:
            like = f"%{q_text.strip()}%"
            q = q.filter(or_(Property.dorm_name.ilike(like), Property.facebook_url.ilike(like)))
        min_price = (filters or {}).get('min_price')
        max_price = (filters or {}).get('max_price')
        if min_price is not None: q = q.filter(Property.rent_price >= int(min_price))
        if max_price is not None: q = q.filter(Property.rent_price <= int(max_price))
        room_type = (filters or {}).get('room_type')
        if room_type: q = q.filter(Property.room_type == room_type)
        availability = (filters or {}).get('availability')
        if availability in {"vacant","occupied"}: q = q.filter(Property.availability_status == availability)
        codes = (filters or {}).get('amenities')
        if codes:
            codes_list = [c.strip() for c in codes.split(',') if c.strip()]
            if codes_list:
                q = (q.join(PropertyAmenity, PropertyAmenity.property_id == Property.id)
                       .join(Amenity, Amenity.id == PropertyAmenity.amenity_id)
                       .filter(Amenity.code.in_(codes_list))
                       .group_by(Property.id)
                       .having(func.count(func.distinct(Amenity.code)) == len(codes_list)))
        return q

    def list_all_paginated(self, search_query=None, page=1, per_page=15):
        from app.extensions import db
        q = Property.query

        if search_query:
            like_filter = f"%{search_query}%"
            q = q.filter(Property.dorm_name.ilike(like_filter))

        return db.paginate(
            q.order_by(Property.created_at.desc()),
            page=page, per_page=per_page, error_out=False
        )
from sqlalchemy import or_, func, not_
from app.models.property import Property, Amenity, PropertyAmenity
from app.extensions import db
from datetime import datetime

class SqlPropertyRepo:
    def get(self, prop_id: int):
        return Property.query.get(prop_id)

    def add(self, prop: Property) -> Property:
        db.session.add(prop)
        db.session.commit()
        return prop

    def save(self, prop: Property):
        db.session.commit()

    def delete(self, prop: Property):
        """ลบ Property ออกจากฐานข้อมูลอย่างถาวร"""
        db.session.delete(prop)
        db.session.commit()

    def list_approved(self, **filters):
        q = Property.query.filter(
            Property.workflow_status == Property.WORKFLOW_APPROVED,
            Property.deleted_at.is_(None)
        ).order_by(Property.created_at.desc())

        # --- vvv ส่วนที่แก้ไขทั้งหมดจะอยู่ในฟังก์ชันนี้ vvv ---

        q_text = (filters or {}).get('q')
        if q_text:
            like = f"%{q_text.strip()}%"
            q = q.filter(Property.dorm_name.ilike(like))
        
        road_text = (filters or {}).get('road')
        if road_text:
            q = q.filter(Property.road.ilike(f"%{road_text.strip()}%"))

        soi_text = (filters or {}).get('soi')
        if soi_text:
            q = q.filter(Property.soi.ilike(f"%{soi_text.strip()}%"))

        min_price = (filters or {}).get('min_price')
        if min_price is not None and min_price.isdigit():
            q = q.filter(Property.rent_price >= int(min_price))

        max_price = (filters or {}).get('max_price')
        if max_price is not None and max_price.isdigit():
            q = q.filter(Property.rent_price <= int(max_price))

        room_type = (filters or {}).get('room_type')
        if room_type:
            # นี่คือตรรกะใหม่ที่เพิ่มเข้ามา
            if room_type == 'other':
                # ถ้าผู้ใช้เลือก "อื่นๆ" ให้ค้นหาทุกประเภทที่ไม่ใช่ประเภทมาตรฐาน
                standard_types = ['standard', 'studio', 'suite']
                q = q.filter(not_(Property.room_type.in_(standard_types)))
            else:
                # ถ้าเลือกประเภทอื่น หรือกรอกข้อความมา ก็ให้ค้นหาตรงๆ
                q = q.filter(Property.room_type.ilike(f"%{room_type.strip()}%"))
        
        availability = (filters or {}).get('availability')
        if availability in {Property.AVAILABILITY_VACANT, Property.AVAILABILITY_OCCUPIED}:
            q = q.filter(Property.availability_status == availability)
        
        codes = (filters or {}).get('amenities')
        if codes:
            codes_list = [c.strip() for c in codes.split(',') if c.strip()]
            if codes_list:
                q = (q.join(PropertyAmenity, PropertyAmenity.property_id == Property.id)
                      .join(Amenity, Amenity.id == PropertyAmenity.amenity_id)
                      .filter(Amenity.code.in_(codes_list))
                      .group_by(Property.id)
                      .having(func.count(func.distinct(Amenity.code)) == len(codes_list)))
        
        # --- ^^^ สิ้นสุดส่วนที่แก้ไข ^^^ ---
        return q

    def list_all_paginated(self, search_query=None, page=1, per_page=15):
        q = Property.query.filter(Property.deleted_at.is_(None))
        if search_query:
            like_filter = f"%{search_query}%"
            q = q.filter(Property.dorm_name.ilike(like_filter))
        return db.paginate(
            q.order_by(Property.id.asc()),
            page=page, per_page=per_page, error_out=False
        )

    def get_deleted_properties_paginated(self, page=1, per_page=15):
        q = Property.query.filter(Property.deleted_at.isnot(None))
        return db.paginate(
            q.order_by(Property.deleted_at.desc()),
            page=page, per_page=per_page, error_out=False
        )

    def count_active_properties(self) -> int:
        return db.session.query(Property).filter(Property.deleted_at.is_(None)).count()

    def count_properties_by_month(self, date_obj: datetime) -> int:
        """
        นับจำนวน Property ที่ถูกสร้างในเดือนที่กำหนด (ใช้ to_char สำหรับ PostgreSQL)
        """
        # แก้ไข: เปลี่ยน func.strftime เป็น func.to_char เพื่อรองรับ PostgreSQL
        return db.session.query(Property).filter(
            func.to_char(Property.created_at, 'YYYY-MM') == date_obj.strftime("%Y-%m")
        ).count()

    def get_property_counts_by_road(self, limit: int = 5):
        return db.session.query(
            Property.road, func.count(Property.id).label('count')
        ).filter(
            Property.road.isnot(None), Property.road != ''
        ).group_by(Property.road).order_by(func.count(Property.id).desc()).limit(limit).all()

    def get_property_counts_by_room_type(self, limit: int = 5):
        """นับจำนวนหอพักตามประเภทห้อง (room_type)"""
        return db.session.query(
            Property.room_type, func.count(Property.id).label('count')
        ).filter(
            Property.room_type.isnot(None), Property.room_type != ''
        ).group_by(Property.room_type).order_by(func.count(Property.id).desc()).limit(limit).all()

    def get_property_counts_by_workflow_status(self):
        """นับจำนวนหอพักในแต่ละสถานะ (workflow_status)"""
        return db.session.query(
            Property.workflow_status, func.count(Property.id).label('count')
        ).filter(Property.deleted_at.is_(None)).group_by(Property.workflow_status).all()
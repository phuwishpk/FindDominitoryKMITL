from sqlalchemy import or_, func, desc, case
from app.models.property import Property, Amenity, PropertyAmenity
from app.extensions import db
from datetime import datetime

class SqlPropertyRepo:
    def get(self, prop_id: int):
        # ดึงข้อมูล Property ที่มีสถานะ approved เท่านั้น
        return Property.query.filter_by(id=prop_id, workflow_status="approved").first()

    def add(self, prop: Property) -> Property:
        db.session.add(prop)
        db.session.commit()
        return prop

    def save(self, prop: Property):
        db.session.commit()

    def delete(self, prop: Property):
        """ลบ Property ออกจากฐานข้อมูลอย่างถาวร (Permanent Delete)"""
        db.session.delete(prop)
        db.session.commit()

    # --- PUBLIC SEARCH FUNCTION (Best Match) ---
    def list_approved(self, **filters):
        """
        คืน SQLAlchemy Query ของประกาศที่ workflow_status='approved'
        พร้อมฟิลเตอร์ q, road, soi, price, amenities และมีการจัดเรียงตามความเกี่ยวข้อง (Relevance)
        """
        q = Property.query.filter(Property.workflow_status == "approved")
        relevance_score_expression = 0
        has_score = False # Flag เพื่อตรวจสอบว่ามีการใช้ Scoring หรือไม่
        
        # 1. Text Search and Scoring
        q_text = filters.get('q')
        road_text = filters.get('road')
        soi_text = filters.get('soi')
        
        if q_text:
            cleaned_q = q_text.strip()
            like = f"%{cleaned_q}%"
            q = q.filter(or_(Property.dorm_name.ilike(like), Property.facebook_url.ilike(like)))
            relevance_score_expression += case([(func.lower(Property.dorm_name) == func.lower(cleaned_q), 100)], else_=0)
            has_score = True

        # 2. Road Filter and Scoring (Best Match)
        if road_text and hasattr(Property, 'road'):
            cleaned_road = road_text.strip()
            like = f"%{cleaned_road}%"
            q = q.filter(Property.road.ilike(like)) 
            relevance_score_expression += case([(func.lower(Property.road) == func.lower(cleaned_road), 20)], else_=0)
            has_score = True

        # 3. Soi Filter and Scoring (Best Match)
        if soi_text and hasattr(Property, 'soi'):
            cleaned_soi = soi_text.strip()
            like = f"%{cleaned_soi}%"
            q = q.filter(Property.soi.ilike(like))
            relevance_score_expression += case([(func.lower(Property.soi) == func.lower(cleaned_soi), 5)], else_=0)
            has_score = True

        # 4. Price range and Room type filters...
        min_price = filters.get('min_price'); max_price = filters.get('max_price')
        if min_price is not None: q = q.filter(Property.rent_price >= int(min_price))
        if max_price is not None: q = q.filter(Property.rent_price <= int(max_price))
        room_type = filters.get('room_type')
        if room_type: q = q.filter(Property.room_type == room_type)
        availability = filters.get('availability')
        if availability in {"vacant", "occupied"}: q = q.filter(Property.availability_status == availability)

        # 5. Amenities Filter and Scoring (ใช้ OR logic และ Group By)
        codes = filters.get('amenities')
        if codes:
            codes_list = [c.strip() for c in codes.split(',') if c.strip()] if isinstance(codes, str) else codes
            if codes_list:
                # ใช้ JOIN + FILTER + GROUP BY เพื่อให้ผลลัพธ์มีอย่างน้อย 1 amenity ที่ตรง
                q = (q.join(PropertyAmenity).join(Amenity)
                     .filter(Amenity.code.in_(codes_list))
                     .group_by(Property.id)
                )
                relevance_score_expression += (func.count(Amenity.code) * 10) 
                has_score = True

        # 6. Final Ordering (FIXED: ป้องกัน ArgumentError)
        if has_score:
            # เรียงตามคะแนนที่คำนวณได้ก่อน
            q = q.order_by(desc(relevance_score_expression), desc(Property.updated_at))
        else:
            # ถ้าไม่มีเงื่อนไขค้นหาที่ให้คะแนน ให้เรียงตามวันที่อัปเดตล่าสุดเท่านั้น
            q = q.order_by(desc(Property.updated_at))

        return q

    # --- ADMIN/DASHBOARD REPOSITORY FUNCTIONS (FIXED) ---
    def list_all_paginated(self, search_query=None, page=1, per_page=15):
        """ดึงรายการ Properties ทั้งหมดสำหรับ Admin"""
        q = Property.query

        if search_query:
            like_filter = f"%{search_query}%"
            q = q.join(Property.owner).filter(or_(
                Property.dorm_name.ilike(like_filter),
                Property.owner.has(Property.owner.full_name_th.ilike(like_filter))
            ))

        return db.paginate(
            q.order_by(desc(Property.created_at)),
            page=page, per_page=per_page, error_out=False
        )
    
    # ... (ส่วน Admin functions อื่น ๆ ถูกรวมอยู่ในโค้ดที่คุณส่งมาล่าสุดแล้ว)
    def get_deleted_properties_paginated(self, page=1, per_page=15):
        if hasattr(Property, 'deleted_at'):
             q = Property.query.filter(Property.deleted_at.isnot(None))
        else:
             q = Property.query.filter(Property.workflow_status.in_(["rejected", "draft"])) 
             
        return db.paginate(
            q.order_by(desc(Property.updated_at)),
            page=page, per_page=per_page, error_out=False
        )
    
    def count_active_properties(self) -> int:
        return db.session.query(Property).filter(Property.workflow_status == "approved").count()
    
    def count_properties_by_month(self, date_obj: datetime) -> int:
        return db.session.query(Property).filter(
            func.strftime('%Y-%m', Property.created_at) == date_obj.strftime("%Y-%m")
        ).count()

    def get_property_counts_by_road(self, limit: int = 5):
        if hasattr(Property, 'road'):
            q = db.session.query(
                Property.road, func.count(Property.id).label('count')
            ).filter(
                Property.road.isnot(None), Property.road != '',
                Property.workflow_status == "approved"
            ).group_by(Property.road).order_by(desc('count')).limit(limit).all()
            return q
        return []

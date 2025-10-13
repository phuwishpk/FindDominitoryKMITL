from sqlalchemy import or_, func, case, desc
from app.models.property import Property, Amenity, PropertyAmenity
from app.extensions import db
from datetime import datetime

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

    def delete(self, prop: Property):
        """ลบ Property ออกจากฐานข้อมูลอย่างถาวร"""
        db.session.delete(prop)
        db.session.commit()

    def list_approved(self, **filters):
        """
        คืน SQLAlchemy Query ของประกาศที่ workflow_status='approved'
        พร้อมฟิลเตอร์ q, road, soi, price_min/max, room_type, amenities
        และมีการจัดเรียงตามความเกี่ยวข้อง (Relevance)
        """
        q = Property.query.filter(
            Property.workflow_status == "approved"
        )
        
        # 0. Relevance Scoring Initialization
        relevance_score = 0
        
        # 1. Filter by text search (q) - ค้นหาจากชื่อหอและให้คะแนน
        q_text = filters.get('q')
        if q_text:
            cleaned_q = q_text.strip()
            like = f"%{cleaned_q}%"
            
            # Filter: ต้องมีคำที่ค้นหาใน dorm_name หรือ facebook_url
            q = q.filter(or_(
                Property.dorm_name.ilike(like),
                Property.facebook_url.ilike(like)
            ))
            
            # Ranking: ให้คะแนน 100 หากชื่อหอตรงกันแบบเป๊ะๆ (Case-insensitive)
            # และให้คะแนน 50 หากคำค้นหาปรากฏในชื่อหอ
            relevance_score += case(
                (func.lower(Property.dorm_name) == func.lower(cleaned_q), 100),
                (Property.dorm_name.ilike(like), 50),
                else_=0
            )


        # 2. Filter by road - ค้นหาจากชื่อถนนและให้คะแนน
        road_text = filters.get('road')
        if road_text:
            cleaned_road = road_text.strip()
            like = f"%{cleaned_road}%"
            
            # NOTE: Assuming Property model has a 'road' column
            q = q.filter(Property.road.ilike(like))

            # Ranking: ให้คะแนน 20 หากถนนตรงกันแบบเป๊ะๆ
            relevance_score += case(
                (func.lower(Property.road) == func.lower(cleaned_road), 20),
                (Property.road.ilike(like), 10),
                else_=0
            )


        # 3. Filter by soi - ค้นหาจากชื่อซอยและให้คะแนน
        soi_text = filters.get('soi')
        if soi_text:
            cleaned_soi = soi_text.strip()
            like = f"%{cleaned_soi}%"
            
            # NOTE: Assuming Property model has a 'soi' column
            q = q.filter(Property.soi.ilike(like))
            
            # Ranking: ให้คะแนน 5 หากซอยตรงกันแบบเป๊ะๆ
            relevance_score += case(
                (func.lower(Property.soi) == func.lower(cleaned_soi), 5),
                (Property.soi.ilike(like), 2),
                else_=0
            )


        # 4. Filter by price range
        min_price = filters.get('min_price')
        max_price = filters.get('max_price')
        if min_price is not None:
            q = q.filter(Property.rent_price >= int(min_price))
        if max_price is not None:
            q = q.filter(Property.rent_price <= int(max_price))

        # 5. Filter by room type
        room_type = filters.get('room_type')
        if room_type:
            q = q.filter(Property.room_type == room_type)

        # 6. Filter by amenities (ต้องมีครบทุกอย่างที่เลือก - AND logic)
        codes = filters.get('amenities')
        if codes:
            # Note: The search_args from the front-end will determine if this is a list or a comma-separated string
            codes_list = [c.strip() for c in codes.split(',') if c.strip()] if isinstance(codes, str) else codes
            if codes_list:
                q = (
                    q.join(PropertyAmenity)
                     .join(Amenity)
                     .filter(Amenity.code.in_(codes_list))
                     .group_by(Property.id)
                     .having(func.count(func.distinct(Amenity.code)) == len(codes_list))
                )
                
                # Ranking: ให้คะแนน 10 ต่อ 1 Amenity ที่ตรง
                relevance_score += (func.count(func.distinct(Amenity.code)) * 10)


        # 7. Sorting: จัดเรียงตามคะแนนความเกี่ยวข้อง (สูงสุดไปต่ำสุด) ก่อน แล้วตามวันที่อนุมัติ
        if isinstance(relevance_score, int) and relevance_score == 0:
            # หากไม่มีการค้นหาใดๆ ที่ต้องให้คะแนน (ไม่มี q, road, soi) ให้เรียงตามเวลาล่าสุดเท่านั้น
            q = q.order_by(desc(Property.updated_at))
        else:
            # หากมีการให้คะแนน ให้เรียงตามคะแนนก่อน แล้วค่อยตามเวลาล่าสุด
            q = q.order_by(desc(relevance_score), desc(Property.approved_at), desc(Property.updated_at))


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
        """ดึงรายการ Properties ที่ถูกลบ (soft-deleted)"""
        q = Property.query.filter(Property.deleted_at.isnot(None))
        return db.paginate(
            q.order_by(Property.deleted_at.desc()),
            page=page, per_page=per_page, error_out=False
        )

    def count_active_properties(self) -> int:
        return db.session.query(Property).filter(Property.deleted_at.is_(None)).count()

    def count_properties_by_month(self, date_obj: datetime) -> int:
        return db.session.query(Property).filter(
            func.strftime('%Y-%m', Property.created_at) == date_obj.strftime("%Y-%m")
        ).count()

    def get_property_counts_by_road(self, limit: int = 5):
        return db.session.query(
            Property.road, func.count(Property.id).label('count')
        ).filter(
            Property.road.isnot(None), Property.road != ''
        ).group_by(Property.road).order_by(func.count(Property.id).desc()).limit(limit).all()
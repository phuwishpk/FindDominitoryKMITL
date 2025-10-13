from sqlalchemy import or_, func, case, desc
from app.models.property import Property, Amenity, PropertyAmenity
from app.extensions import db
from datetime import datetime

class SqlPropertyRepo:
    def get(self, prop_id: int):
        # ดึงข้อมูล Property ที่มีสถานะ approved เท่านั้น
        return Property.query.filter_by(id=prop_id, workflow_status="approved").first()

    def add(self, prop: Property) -> Property:
        # บันทึก property ใหม่
        db.session.add(prop)
        db.session.commit()
        return prop

    def save(self, prop: Property):
        # บันทึกการเปลี่ยนแปลง
        db.session.commit()

    def list_approved(self, **filters):
        """
        คืน SQLAlchemy Query ของประกาศที่ workflow_status='approved'
        พร้อมฟิลเตอร์ q, road, soi, price_min/max, room_type, amenities
        และมีการจัดเรียงตามความเกี่ยวข้อง (Relevance)
        """
        q = Property.query.filter(Property.workflow_status == "approved")
        
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
            
            # Ranking: ให้คะแนน 100 หากชื่อหอตรงกันแบบเป๊ะๆ 
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
            
            # Filter: ต้องมีคำที่ค้นหาใน road (สมมติว่า model มี 'road' column)
            # NOTE: ถ้า model ไม่มี 'road' หรือ 'soi' จะต้องสร้าง migration เพิ่มคอลัมน์ก่อน
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
            
            # Filter: ต้องมีคำที่ค้นหาใน soi
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
            codes_list = [c.strip() for c in codes.split(',') if c.strip()]
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
            # Default sorting: เรียงตามวันที่อัปเดตล่าสุด
            q = q.order_by(desc(Property.updated_at))
        else:
            # Relevance sorting: เรียงตามคะแนนก่อน แล้วตามวันที่ล่าสุด
            q = q.order_by(desc(relevance_score), desc(Property.approved_at), desc(Property.updated_at))

        return q
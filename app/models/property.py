from datetime import datetime
from app.extensions import db

# --- association table: many-to-many (Property <-> Amenity)
# เปลี่ยนจาก db.Table เป็น "Model class" เพื่อให้ที่อื่น import PropertyAmenity ได้
class PropertyAmenity(db.Model):
    __tablename__ = "property_amenities"
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id"), primary_key=True)
    amenity_id  = db.Column(db.Integer, db.ForeignKey("amenities.id"), primary_key=True)

class Amenity(db.Model):
    __tablename__ = "amenities"

    id        = db.Column(db.Integer, primary_key=True)
    code      = db.Column(db.String(50), unique=True, nullable=False, index=True)
    label_th  = db.Column(db.String(120), nullable=False)
    label_en  = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<Amenity {self.code}>"

class Property(db.Model):
    __tablename__ = "properties"

    # ---- ค่าคงที่สถานะ workflow (ให้สอดคล้องกับ services/approval)
    WORKFLOW_DRAFT     = "draft"
    WORKFLOW_PENDING   = "pending"
    WORKFLOW_SUBMITTED = "submitted"
    WORKFLOW_APPROVED  = "approved"
    WORKFLOW_REJECTED  = "rejected"

    id = db.Column(db.Integer, primary_key=True)

    # เจ้าของ
    owner_id = db.Column(db.Integer, index=True, nullable=False)

    # เนื้อหา/ราคา/ประเภท (คง field เดิม + เพิ่ม field ที่ services/seed ใช้)
    title         = db.Column(db.String(200), nullable=False)    # ใช้แทน dorm_name
    description   = db.Column(db.Text, nullable=True)
    price         = db.Column(db.Float, index=True, nullable=True)        # ใช้แทน rent_price
    property_type = db.Column(db.String(50), index=True, nullable=True)   # ใช้แทน room_type

    # เพื่อความเข้ากันได้กับ services เดิม (optional เผื่อคุณยังอ้างชื่อนี้บางจุด)
    room_type  = db.Column(db.String(50), index=True, nullable=True)   # mirror ไปยัง property_type ได้ใน service
    rent_price = db.Column(db.Float, index=True, nullable=True)        # mirror ไปยัง price ได้ใน service

    # ที่อยู่/พิกัด
    address_line = db.Column(db.String(255), nullable=True)
    road = db.Column(db.String(120), nullable=True)
    soi = db.Column(db.String(120), nullable=True)
    subdistrict = db.Column(db.String(120), index=True, nullable=True)
    district = db.Column(db.String(120), index=True, nullable=True)
    province = db.Column(db.String(120), index=True, nullable=True)
    postal_code = db.Column(db.String(10), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    # GeoJSON pin ที่ services ใช้
    location_pin = db.Column(db.JSON, nullable=True)

    # สถานะ/อนุมัติ/ใช้งาน
    status       = db.Column(db.String(30), index=True, default="active")  # active|hidden|draft (ของเก่า)
    is_approved  = db.Column(db.Boolean, index=True, default=False)        # ของเก่า (คงไว้เพื่อเข้ากันได้)
    is_active    = db.Column(db.Boolean, index=True, default=True)

    # สถานะ workflow ที่ services/approval_service ใช้จริง
    workflow_status = db.Column(db.String(20), index=True, default=WORKFLOW_DRAFT)

    # เวลา
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # ความสัมพันธ์กับ Amenity (อ้าง secondary เป็น __tablename__)
    amenities = db.relationship(
        "Amenity",
        secondary="property_amenities",
        backref=db.backref("properties", lazy="dynamic"),
        lazy="selectin",
    )

    __table_args__ = (
        db.Index("ix_properties_loc", "province", "district", "subdistrict"),
        db.Index("ix_properties_status_approved", "status", "is_approved"),
        db.Index("ix_properties_workflow", "workflow_status"),
    )

    def __repr__(self) -> str:
        return f"<Property {self.id} {self.title!r}>"

    def to_dict(self):
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "property_type": self.property_type,
            "room_type": self.room_type,
            "rent_price": self.rent_price,
            "address_line": self.address_line,
            "road": self.road,
            "soi": self.soi,
            "subdistrict": self.subdistrict,
            "district": self.district,
            "province": self.province,
            "postal_code": self.postal_code,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "location_pin": self.location_pin,
            "status": self.status,
            "is_approved": self.is_approved,
            "is_active": self.is_active,
            "workflow_status": self.workflow_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            # ⬇️ เดิมใช้ a.name (ไม่มี) → ปรับให้ส่ง code และ label
            "amenities": [{"code": a.code, "label_th": a.label_th, "label_en": a.label_en} for a in self.amenities],
        }

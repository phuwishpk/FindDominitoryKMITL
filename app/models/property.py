from datetime import datetime
from app.extensions import db
from app.models.review import Review 

class PropertyAmenity(db.Model):
    __tablename__ = "property_amenities"
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    amenity_id = db.Column(db.Integer, db.ForeignKey("amenities.id", ondelete="CASCADE"), nullable=False)
    __table_args__ = (db.UniqueConstraint("property_id", "amenity_id", name="uq_property_amenity"),)

class Amenity(db.Model):
    __tablename__ = "amenities"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), unique=True, nullable=False)
    label_th = db.Column(db.String(120), nullable=False)
    label_en = db.Column(db.String(120))

    def __repr__(self) -> str:
        return f"<Amenity {self.code}>"

class Property(db.Model):
    __tablename__ = "properties"

    # ค่าคงที่สำหรับ workflow_status
    WORKFLOW_DRAFT = "draft"
    WORKFLOW_SUBMITTED = "submitted"
    WORKFLOW_APPROVED = "approved"
    WORKFLOW_REJECTED = "rejected"

    # ค่าคงที่สำหรับ availability_status
    AVAILABILITY_VACANT = "vacant"
    AVAILABILITY_OCCUPIED = "occupied"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("owners.id", ondelete="CASCADE"), nullable=False)
    dorm_name = db.Column(db.String(120), nullable=False)
    road = db.Column(db.String(255), nullable=True)
    soi = db.Column(db.String(255), nullable=True)
    room_type = db.Column(db.String(30), nullable=False)
    contact_phone = db.Column(db.String(20))
    line_id = db.Column(db.String(80))
    facebook_url = db.Column(db.String(255))
    location_pin = db.Column(db.JSON, nullable=True)
    rent_price = db.Column(db.Integer)
    water_rate = db.Column(db.Float)
    electric_rate = db.Column(db.Float)
    deposit_amount = db.Column(db.Integer)
    additional_info = db.Column(db.Text, nullable=True)
    availability_status = db.Column(db.String(16), default=AVAILABILITY_VACANT)
    workflow_status = db.Column(db.String(16), default=WORKFLOW_DRAFT)
    approved_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
    reviews = db.relationship(
    "Review",  # ชื่อ Model รีวิว
    backref="property",  # ให้ฝั่ง Review เข้าถึง property ได้
    lazy="dynamic",  # ดึงเฉพาะเมื่อใช้ query
    cascade="all, delete-orphan"  # ลบหอพัก -> รีวิวหายตาม
)

    reviews = db.relationship("Review", backref="property", cascade="all, delete-orphan", lazy=True)
    images = db.relationship(
        "PropertyImage",
        back_populates="property",
        cascade="all, delete-orphan",
        order_by="PropertyImage.position.asc()"
    )
    amenities = db.relationship(
        "Amenity",
        secondary="property_amenities",
        backref=db.backref("properties", lazy="dynamic"),
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return f"<Property id={self.id} owner={self.owner_id} name={self.dorm_name!r}>"

class PropertyImage(db.Model):
    __tablename__ = "property_images"
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    position = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    property = db.relationship("Property", back_populates="images")

    def __repr__(self) -> str:
        return f"<PropertyImage id={self.id} prop={self.property_id} pos={self.position}>"
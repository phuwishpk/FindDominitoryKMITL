import json
from app.models.property import Property, Amenity
from app.models.approval import AuditLog
from app.extensions import db
from .location_service import LocationDataHandler

class PropertyService:
    def __init__(self, repo):
        self.repo = repo
        self.location_handler = LocationDataHandler()

    def _prepare_data(self, data: dict) -> dict:
        """
        ฟังก์ชัน Helper เพื่อจัดการข้อมูล room_type และ location_pin ก่อนบันทึก
        """
        if data.get('room_type') == 'อื่นๆ':
            other_type = data.get('other_room_type', '').strip()
            if other_type:
                data['room_type'] = other_type
        
        data.pop('other_room_type', None)

        location_json_str = data.pop('location_pin_json', None)
        data['location_pin'] = self.location_handler.parse_geojson_string(location_json_str)
        
        return data

    def create(self, owner_id: int, data: dict) -> Property:
        amenity_codes = data.pop('amenities', [])
        data.pop('images', None)
        
        prepared_data = self._prepare_data(data)

        prop = Property(owner_id=owner_id, **prepared_data)
        if amenity_codes:
            amenities = Amenity.query.filter(Amenity.code.in_(amenity_codes)).all()
            prop.amenities = amenities
        return self.repo.add(prop)

    def update(self, owner_id: int, prop_id: int, data: dict):
        prop = self.repo.get(prop_id)
        if not prop or prop.owner_id != owner_id:
            return None

        # --- vvv ส่วนที่เพิ่มเข้ามา: ตรวจสอบสถานะก่อนแก้ไข ---
        was_approved = prop.workflow_status == Property.WORKFLOW_APPROVED
        # --- ^^^ สิ้นสุดการแก้ไข ^^^ ---

        amenity_codes = data.pop('amenities', [])
        data.pop('images', None)
        prepared_data = self._prepare_data(data)

        for k, v in prepared_data.items():
            setattr(prop, k, v)

        if amenity_codes:
            amenities = Amenity.query.filter(Amenity.code.in_(amenity_codes)).all()
            prop.amenities = amenities
        else:
            prop.amenities = []
        
        # --- vvv ส่วนที่เพิ่มเข้ามา: เปลี่ยนสถานะกลับเป็น draft ถ้าเคย approved แล้ว ---
        if was_approved:
            prop.workflow_status = Property.WORKFLOW_DRAFT
        # --- ^^^ สิ้นสุดการแก้ไข ^^^ ---

        log_entry = AuditLog.log(
            actor_type="owner",
            actor_id=owner_id,
            action="update_property",
            property_id=prop_id,
            meta={"details": "Owner updated property info."}
        )
        db.session.add(log_entry)

        self.repo.save(prop)
        return prop
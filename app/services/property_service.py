# app/services/property_service.py
from __future__ import annotations
from typing import TYPE_CHECKING

from app.extensions import db
from .location_service import LocationDataHandler

if TYPE_CHECKING:
    # ใช้เพื่อ type-check เท่านั้น ไม่รันตอน runtime (กันวงจรอิมพอร์ต)
    from app.models.property import Property

class PropertyService:
    def __init__(self, repo):
        self.repo = repo
        self.location_handler = LocationDataHandler()

    def _prepare_data(self, data: dict) -> dict:
        """
        จัดการข้อมูล room_type และ location_pin ก่อนบันทึก
        """
        # map room_type 'อื่นๆ' -> ค่า other_room_type (ถ้ามี)
        if data.get('room_type') == 'อื่นๆ':
            other_type = (data.get('other_room_type') or '').strip()
            if other_type:
                data['room_type'] = other_type
        data.pop('other_room_type', None)

        # parse GeoJSON จากฟอร์ม
        location_json_str = data.pop('location_pin_json', None)
        data['location_pin'] = self.location_handler.parse_geojson_string(location_json_str)

        return data

    def create(self, owner_id: int, data: dict) -> "Property":
        # ✅ lazy import เพื่อตัดวงจรอิมพอร์ต
        from app.models.property import Property, Amenity

        amenity_codes = data.pop('amenities', []) or []
        data.pop('images', None)  # รูปภาพไปจัดการที่ upload/another service

        prepared_data = self._prepare_data(data)

        prop = Property(owner_id=owner_id, **prepared_data)

        if amenity_codes:
            # ระวัง: Amenity ต้องมี field 'code'
            amenities = Amenity.query.filter(Amenity.code.in_(amenity_codes)).all()
            prop.amenities = amenities

        return self.repo.add(prop)

    def update(self, owner_id: int, prop_id: int, data: dict):
        # ✅ lazy import
        from app.models.property import Amenity
        from app.models.approval import AuditLog

        prop = self.repo.get(prop_id)
        if not prop or prop.owner_id != owner_id:
            return None

        amenity_codes = data.pop('amenities', []) or []
        data.pop('images', None)

        prepared_data = self._prepare_data(data)

        for k, v in prepared_data.items():
            setattr(prop, k, v)

        if amenity_codes:
            amenities = Amenity.query.filter(Amenity.code.in_(amenity_codes)).all()
            prop.amenities = amenities
        else:
            prop.amenities = []

        # บันทึก AuditLog เข้า session (repo.save จะ commit ให้)
        log_entry = AuditLog.log(
            actor_type="owner",
            actor_id=owner_id,
            action="update_property",
            property_id=prop_id,
            meta={"details": "Owner updated property info."},
        )
        db.session.add(log_entry)

        self.repo.save(prop)  # .save() ควร commit session
        return prop

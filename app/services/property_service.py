# app/services/policies/property_policy.py

class PropertyPolicy:
    """
    คลาสสำหรับจัดการนโยบายและกฎเกณฑ์ที่เกี่ยวกับหอพัก (Property)
    """
    # กำหนดจำนวนรูปภาพสูงสุดที่อนุญาตให้อัปโหลดได้
    MAX_IMAGES: int = 6

    @staticmethod
    def can_upload_more(current_count: int) -> bool:
        """
        ตรวจสอบว่าเจ้าของหอพักสามารถอัปโหลดรูปภาพเพิ่มเติมได้หรือไม่
        โดยเปรียบเทียบจำนวนรูปภาพปัจจุบันกับจำนวนสูงสุดที่อนุญาต

        Args:
            current_count (int): จำนวนรูปภาพปัจจุบันของหอพัก

        Returns:
            bool: True ถ้ายังสามารถอัปโหลดเพิ่มได้, False ถ้าถึงขีดจำกัดแล้ว
        """
        return current_count < PropertyPolicy.MAX_IMAGES


# app/services/property_service.py

from app.models.property import Property, Amenity
from app.extensions import db

class PropertyService:
    """
    Service สำหรับจัดการตรรกะทางธุรกิจของ Property (หอพัก)
    """
    def __init__(self, repo):
        self.repo = repo

    def create(self, owner_id: int, data: dict) -> Property:
        """
        สร้าง Property ใหม่
        """
        prop = Property(owner_id=owner_id, **data)
        return self.repo.add(prop)

    def update(self, owner_id: int, prop_id: int, data: dict):
        """
        อัปเดตข้อมูล Property
        """
        prop = self.repo.get(prop_id)
        if not prop or prop.owner_id != owner_id:
            return None
        for k, v in data.items():
            setattr(prop, k, v)
        self.repo.save(prop)
        return prop

    def update_property_amenities(self, prop: Property, amenity_ids: list[int]) -> None:
        """
        อัปเดตสิ่งอำนวยความสะดวก (Amenities) ของหอพัก
        จัดการความสัมพันธ์แบบ Many-to-Many

        Args:
            prop (Property): อ็อบเจกต์ของหอพักที่ต้องการอัปเดต
            amenity_ids (list[int]): ID ของ Amenities ที่ถูกเลือกจากฟอร์ม
        """
        # 1. ล้างข้อมูล Amenity เดิมทั้งหมดของหอพักนี้
        prop.amenities.clear()

        # 2. ดึงข้อมูล Amenity ทั้งหมดจาก DB ตาม ID ที่ได้รับ
        selected_amenities = Amenity.query.filter(Amenity.id.in_(amenity_ids)).all()

        # 3. เพิ่ม Amenity ใหม่เข้าไปในหอพัก
        for amenity in selected_amenities:
            prop.amenities.append(amenity)

        # 4. บันทึกการเปลี่ยนแปลงลงฐานข้อมูล
        self.repo.save(prop)
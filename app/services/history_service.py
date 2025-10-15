from flask import session
from app.models.property import Property
from app.repositories.interfaces.property_repo import IPropertyRepo

class HistoryService:
    """
    จัดการตรรกะสำหรับระบบ "หอพักที่เพิ่งเข้าชม (Recently Viewed)"
    โดยใช้ session ของ Flask ในการจัดเก็บข้อมูล
    """
    SESSION_KEY = 'recently_viewed'
    MAX_HISTORY_SIZE = 5  # จำนวนหอพักสูงสุดที่จะจดจำ

    def __init__(self, property_repo: IPropertyRepo):
        """
        Constructor ของ Service ที่ต้องใช้ PropertyRepository
        ในการดึงข้อมูลหอพักจาก ID ที่เก็บไว้ใน session
        """
        self.property_repo = property_repo

    def add_viewed_property(self, prop_id: int):
        """
        เพิ่ม ID ของหอพักที่เพิ่งเข้าชมลงใน session
        - ถ้ามี ID นี้อยู่แล้ว จะย้ายไปไว้ข้างหน้าสุด (ล่าสุด)
        - รายการจะถูกจำกัดขนาดตาม MAX_HISTORY_SIZE
        """
        # ดึงรายการ ID เดิมจาก session, ถ้าไม่มีให้สร้าง list ว่าง
        viewed_ids = session.get(self.SESSION_KEY, [])

        # ถ้า ID นี้มีอยู่แล้วใน list ให้ลบออกก่อน เพื่อจะย้ายไปไว้ข้างหน้า
        if prop_id in viewed_ids:
            viewed_ids.remove(prop_id)

        # เพิ่ม ID ใหม่เข้าไปข้างหน้าสุดของ list (เป็นรายการล่าสุด)
        viewed_ids.insert(0, prop_id)

        # จำกัดจำนวนประวัติให้ไม่เกินค่าสูงสุดที่กำหนด
        session[self.SESSION_KEY] = viewed_ids[:self.MAX_HISTORY_SIZE]
        session.modified = True  # แจ้งให้ Flask ทราบว่า session มีการเปลี่ยนแปลง

    def get_viewed_properties(self) -> list[Property]:
        """
        ดึงข้อมูลหอพัก (Object) ตาม ID ที่เก็บไว้ใน session
        - คืนค่าเป็น list ของ Property object ที่เรียงลำดับตามการเข้าชมล่าสุด
        - หากไม่มีประวัติ จะคืนค่าเป็น list ว่าง
        """
        viewed_ids = session.get(self.SESSION_KEY, [])
        if not viewed_ids:
            return []

        # ใช้ repository เพื่อดึงข้อมูล Property ทั้งหมดจาก list ของ ID
        # โดยไม่สนใจลำดับในตอนแรก
        properties = self.property_repo.list_approved().filter(Property.id.in_(viewed_ids)).all()

        # สร้าง dictionary mapping จาก id -> property object เพื่อให้ค้นหาได้เร็ว
        prop_map = {prop.id: prop for prop in properties}

        # เรียงลำดับ object ของ Property ตามลำดับ ID ที่อยู่ใน session
        # เพื่อให้รายการที่แสดงผลเป็น "ล่าสุด" ก่อนเสมอ
        ordered_properties = [prop_map[id] for id in viewed_ids if id in prop_map]

        return ordered_properties

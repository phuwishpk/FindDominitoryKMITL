# [FIXED] ลบการนำเข้าโมเดลออกจากส่วนบนของไฟล์
# from app.models.property import Property, Amenity
from app.extensions import db

class PropertyService:
    def __init__(self, repo):
        self.repo = repo

    def create(self, owner_id: int, data: dict):
        from app.models.property import Property # FIX: Import inside method
        prop = Property(owner_id=owner_id, **data)
        return self.repo.add(prop)

    def update(self, owner_id: int, prop_id: int, data: dict):
        from app.models.property import Property # FIX: Import inside method
        prop = self.repo.get(prop_id)
        if not prop or prop.owner_id != owner_id:
            return None
        for k,v in data.items():
            # ตรวจสอบการตั้งค่า Road/Soi เพื่อให้สอดคล้องกับ Model
            if k == 'road' and not hasattr(prop, 'road'): continue
            if k == 'soi' and not hasattr(prop, 'soi'): continue
            
            setattr(prop, k, v)
        self.repo.save(prop)
        return prop
from app.models.property import Property, Amenity
from app.extensions import db

class PropertyService:
    def __init__(self, repo):
        self.repo = repo

    def create(self, owner_id: int, data: dict) -> Property:
        # แยกข้อมูล amenities ออกมาก่อน (ถ้ามี)
        amenity_codes = data.pop('amenities', [])
        
        prop = Property(owner_id=owner_id, **data)
        
        # เพิ่ม amenities
        if amenity_codes:
            amenities = Amenity.query.filter(Amenity.code.in_(amenity_codes)).all()
            for amenity in amenities:
                prop.amenities.append(amenity)

        return self.repo.add(prop)

    def update(self, owner_id: int, prop_id: int, data: dict):
        prop = self.repo.get(prop_id)
        if not prop or prop.owner_id != owner_id:
            return None
        
        # แยกข้อมูล amenities ออกมา
        amenity_codes = data.pop('amenities', [])

        # อัปเดตฟิลด์อื่นๆ
        for k, v in data.items():
            setattr(prop, k, v)
            
        # อัปเดต amenities
        if amenity_codes:
            prop.amenities.clear() # ล้างของเก่าออกก่อน
            amenities = Amenity.query.filter(Amenity.code.in_(amenity_codes)).all()
            for amenity in amenities:
                prop.amenities.append(amenity)

        self.repo.save(prop)
        return prop
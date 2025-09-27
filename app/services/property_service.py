from app.models.property import Property
from app.extensions import db

class PropertyService:
    def __init__(self, repo):
        self.repo = repo

    def create(self, owner_id: int, data: dict) -> Property:
        prop = Property(owner_id=owner_id, **data)
        return self.repo.add(prop)

    def update(self, owner_id: int, prop_id: int, data: dict):
        prop = self.repo.get(prop_id)
        if not prop or prop.owner_id != owner_id:
            return None
        for k,v in data.items():
            setattr(prop, k, v)
        self.repo.save(prop)
        return prop
    
    # (เสริม) M2M amenities
    def update_property_amenities(self, prop: Property, amenity_codes: list[str]) -> None:
        from app.models.property import Amenity
        
        # Clear existing amenities
        prop.amenities = []
        
        # Add new amenities
        if amenity_codes:
            amenities = Amenity.query.filter(Amenity.code.in_(amenity_codes)).all()
            for amenity in amenities:
                prop.amenities.append(amenity)
        
        db.session.commit()
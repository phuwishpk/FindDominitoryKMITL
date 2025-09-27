from app.models.property import Property, Amenity
from app.extensions import db

class PropertyService:
    def __init__(self, repo):
        self.repo = repo

    def create(self, owner_id: int, data: dict) -> Property:
        amenity_codes = data.pop('amenities', [])
        prop = Property(owner_id=owner_id, **data)
        if amenity_codes:
            amenities = Amenity.query.filter(Amenity.code.in_(amenity_codes)).all()
            prop.amenities = amenities
        return self.repo.add(prop)

    def update(self, owner_id: int, prop_id: int, data: dict):
        prop = self.repo.get(prop_id)
        if not prop or prop.owner_id != owner_id:
            return None
        amenity_codes = data.pop('amenities', [])
        for k, v in data.items():
            setattr(prop, k, v)
        if amenity_codes:
            amenities = Amenity.query.filter(Amenity.code.in_(amenity_codes)).all()
            prop.amenities = amenities
        else:
            prop.amenities = []
        self.repo.save(prop)
        return prop
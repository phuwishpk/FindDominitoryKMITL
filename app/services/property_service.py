# app/services/property_service.py
import json # Add this if not present
from app.models.property import Property, Amenity
from app.extensions import db
from .location_service import LocationDataHandler # Import our new class

class PropertyService:
    def __init__(self, repo):
        self.repo = repo
        self.location_handler = LocationDataHandler() # Instantiate the handler

    def create(self, owner_id: int, data: dict) -> Property:
        amenity_codes = data.pop('amenities', [])

        # Handle location pin data
        location_json_str = data.pop('location_pin_json', None)
        data['location_pin'] = self.location_handler.parse_geojson_string(location_json_str)

        prop = Property(owner_id=owner_id, **data)
        if amenity_codes:
            amenities = Amenity.query.filter(Amenity.code.in_(amenity_codes)).all()
            prop.amenities = amenities
        return self.repo.add(prop)

    def update(self, owner_id: int, prop_id: int, data: dict):
        prop = self.repo.get(prop_id)
        if not prop or prop.owner_id != owner_id:
            return None

        # Handle location pin data
        location_json_str = data.pop('location_pin_json', None)
        data['location_pin'] = self.location_handler.parse_geojson_string(location_json_str)

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
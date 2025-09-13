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

from typing import Optional, Sequence
from app.extensions import db
from app.models.property import Property
from app.repositories.interfaces.property_repo import IPropertyRepo


class SqlPropertyRepo(IPropertyRepo):
    def get(self, prop_id: int) -> Optional[Property]:
        return Property.query.get(prop_id)


def add(self, prop: Property) -> Property:
    db.session.add(prop)
    db.session.commit()
    return prop


def save(self, prop: Property) -> None:
    db.session.commit()


def list_approved(self, **filters) -> Sequence[Property]:
    q = Property.query.filter_by(workflow_status="approved")
    # TODO: apply filters (price, room_type, amenities, availability, near...)
    return q.all()
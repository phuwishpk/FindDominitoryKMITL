from typing import Optional, Sequence, Any, Dict
from sqlalchemy import and_, or_, func
from app.extensions import db
from app.models.property import Property, Amenity, PropertyAmenity
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
q = Property.query.filter(Property.workflow_status == "approved")


q_text = (filters or {}).get('q')
if q_text:
like = f"%{q_text.strip()}%"
q = q.filter(or_(Property.dorm_name.ilike(like), Property.facebook_url.ilike(like)))


min_price = (filters or {}).get('min_price')
max_price = (filters or {}).get('max_price')
if min_price is not None:
q = q.filter(Property.rent_price >= int(min_price))
if max_price is not None:
q = q.filter(Property.rent_price <= int(max_price))


room_type = (filters or {}).get('room_type')
if room_type:
q = q.filter(Property.room_type == room_type)


availability = (filters or {}).get('availability')
if availability in {"vacant", "occupied"}:
q = q.filter(Property.availability_status == availability)


# amenities: comma-separated codes -> inner join and HAVING count
codes = (filters or {}).get('amenities')
if codes:
codes_list = [c.strip() for c in codes.split(',') if c.strip()]
if codes_list:
q = (q.join(PropertyAmenity, PropertyAmenity.property_id == Property.id)
.join(Amenity, Amenity.id == PropertyAmenity.amenity_id)
.filter(Amenity.code.in_(codes_list))
.group_by(Property.id)
.having(func.count(func.distinct(Amenity.code)) == len(codes_list)))


# near: simple bounding-box + haversine filter (approx)
near = (filters or {}).get('near') # "lat,lng"
radius_km = (filters or {}).get('radius_km')
if near and radius_km:
try:
lat0, lng0 = [float(x) for x in near.split(',')]
R = 6371.0
# haversine distance in SQL
dlat = func.radians(Property.lat - lat0)
dlng = func.radians(Property.lng - lng0)
a = func.pow(func.sin(dlat/2), 2) + func.cos(func.radians(lat0)) * func.cos(func.radians(Property.lat)) * func.pow(func.sin(dlng/2), 2)
distance = 2 * R * func.atan2(func.sqrt(a), func.sqrt(1 - a))
q = q.filter(distance <= float(radius_km))
except Exception:
pass


# order by recent approved or price asc
sort = (filters or {}).get('sort')
if sort == 'price_asc':
q = q.order_by(Property.rent_price.asc().nulls_last())
elif sort == 'price_desc':
q = q.order_by(Property.rent_price.desc().nulls_last())
else:
q = q.order_by(Property.approved_at.desc().nulls_last())


return q
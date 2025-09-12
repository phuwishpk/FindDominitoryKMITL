from dataclasses import dataclass


@dataclass
class PropertyCardDTO:
    id: int
    dorm_name: str
    price: int | None
    availability: str
    cover: str | None
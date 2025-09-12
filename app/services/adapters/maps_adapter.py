from typing import Protocol


class IMapsAdapter(Protocol):
    def validate_place(self, place_id: str) -> bool: ...
# app/services/location_service.py
import json
from typing import Optional, Dict

class LocationDataHandler:
    """A class to handle location data transformations."""

    def parse_geojson_string(self, json_string: Optional[str]) -> Optional[Dict]:
        """
        Parses a JSON string into a Python dictionary.
        Returns None if the string is empty or invalid.
        """
        if not json_string:
            return None
        try:
            return json.loads(json_string)
        except json.JSONDecodeError:
            return None # Or raise a custom exception
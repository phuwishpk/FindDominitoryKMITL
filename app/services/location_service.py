import os
from opencage.geocoder import OpenCageGeocode

# แก้ไขชื่อคลาสจาก locationService เป็น LocationService
class LocationService:
    def __init__(self):
        self.api_key = os.getenv("OPENCAGE_API_KEY")
        if not self.api_key:
            raise ValueError("OPENCAGE_API_KEY is not set in the environment variables.")
        self.geocoder = OpenCageGeocode(self.api_key)

    def get_lat_lng(self, location_data: dict) -> tuple[float | None, float | None]:
        # สร้าง query string จากข้อมูลตำแหน่ง
        address_parts = [
            location_data.get("address"),
            location_data.get("road"),
            location_data.get("subdistrict"),
            location_data.get("district"),
            location_data.get("province"),
            location_data.get("zip_code")
        ]
        query = ", ".join(filter(None, address_parts))

        if not query:
            return None, None

        try:
            results = self.geocoder.geocode(query, countrycode='th', language='th')
            if results and len(results):
                lat = results[0]['geometry']['lat']
                lng = results[0]['geometry']['lng']
                return lat, lng
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None, None
        
        return None, None
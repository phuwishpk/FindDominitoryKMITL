class GeoHelper:
    """
    A helper class for geographical-related functionalities, such as generating map URLs.
    """
    @staticmethod
    def build_gmap_embed(lat: float, lng: float, place_id: str | None = None) -> str:
        """
        Constructs a Google Maps embed URL from latitude and longitude coordinates.

        Args:
            lat: The latitude coordinate.
            lng: The longitude coordinate.
            place_id: An optional Google Maps Place ID for a more precise location.

        Returns:
            A string containing the Google Maps embed URL.
        """
        base_url = "https://www.google.com/maps/embed/v1/place"
        query_params = f"q={lat},{lng}"
        if place_id:
            query_params = f"q=place_id:{place_id}"
        
        # Note: You would typically get the API key from a secure configuration
        api_key = "YOUR_GOOGLE_MAPS_API_KEY"  # Replace with your actual API key
        
        return f"{base_url}?key={api_key}&{query_params}"
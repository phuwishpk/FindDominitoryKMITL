from flask import current_app


def google_maps_script_tag() -> str:
    key = current_app.config.get("GOOGLE_MAPS_API_KEY", "")
    return f"https://maps.googleapis.com/maps/api/js?key={key}&libraries=places"
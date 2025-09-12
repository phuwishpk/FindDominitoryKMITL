class PropertyPolicy:
    """Policy สำหรับการจัดการรูปภาพของหอพัก/ห้อง"""
    MAX_IMAGES: int = 6

    @staticmethod
    def can_upload_more(current_count: int) -> bool:
        return current_count < PropertyPolicy.MAX_IMAGES

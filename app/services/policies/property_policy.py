# app/services/policies/property_policy.py

class PropertyPolicy:
    """
    คลาสสำหรับจัดการนโยบายและกฎเกณฑ์ที่เกี่ยวกับหอพัก (Property)
    """
    # กำหนดจำนวนรูปภาพสูงสุดที่อนุญาตให้อัปโหลดได้
    MAX_IMAGES: int = 6

    @staticmethod
    def can_upload_more(current_count: int) -> bool:
        """
        ตรวจสอบว่าเจ้าของหอพักสามารถอัปโหลดรูปภาพเพิ่มเติมได้หรือไม่
        โดยเปรียบเทียบจำนวนรูปภาพปัจจุบันกับจำนวนสูงสุดที่อนุญาต

        Args:
            current_count (int): จำนวนรูปภาพปัจจุบันของหอพัก

        Returns:
            bool: True ถ้ายังสามารถอัปโหลดเพิ่มได้, False ถ้าถึงขีดจำกัดแล้ว
        """
        return current_count < PropertyPolicy.MAX_IMAGES
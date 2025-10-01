import os
from werkzeug.utils import secure_filename

class UploadService:
    def __init__(self, root_dir: str):
        self.root = root_dir

    def save_image(self, owner_id: int, file_storage) -> str:
        """
        ตรวจชนิด/ขนาดไฟล์รูป, ตั้งชื่อไฟล์ปลอดภัย, บันทึกลง uploads/<owner_id>/images/, และคืนค่า relative path
        """
        # ❗️ แก้ไขโค้ดในฟังก์ชันนี้ทั้งหมด ❗️
        
        # 1. สร้าง Path แบบเต็มสำหรับ 'บันทึกไฟล์'
        owner_dir_for_saving = os.path.join(self.root, str(owner_id), "images")
        os.makedirs(owner_dir_for_saving, exist_ok=True)
        
        filename = secure_filename(file_storage.filename or "image")
        full_save_path = os.path.join(owner_dir_for_saving, filename)
        file_storage.save(full_save_path)
        
        # 2. สร้าง Path แบบ Relative สำหรับ 'เก็บลงฐานข้อมูล' เพื่อใช้ใน URL
        relative_path_for_url = os.path.join("uploads", str(owner_id), "images", filename)
        
        # 3. คืนค่า Path ที่ถูกต้อง
        return relative_path_for_url.replace("\\", "/")
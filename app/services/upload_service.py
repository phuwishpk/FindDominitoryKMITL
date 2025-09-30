import os
from werkzeug.utils import secure_filename

class UploadService:
    def __init__(self, root_dir: str):
        self.root = root_dir

    def save_image(self, owner_id: int, file_storage) -> str:
        # สร้าง Path แบบเต็มสำหรับบันทึกไฟล์ลงดิสก์ (ส่วนนี้ถูกต้องแล้ว)
        owner_dir_for_saving = os.path.join(self.root, str(owner_id), "images")
        os.makedirs(owner_dir_for_saving, exist_ok=True)
        
        filename = secure_filename(file_storage.filename or "image")
        full_save_path = os.path.join(owner_dir_for_saving, filename)
        file_storage.save(full_save_path)
        
        # --- แก้ไขส่วนนี้ ---
        # สร้าง Path แบบ Relative โดยให้ขึ้นต้นด้วย "uploads"
        relative_path_for_url = os.path.join("uploads", str(owner_id), "images", filename)
        
        # คืนค่า Path แบบ Relative ที่ใช้ Slash (/)
        return relative_path_for_url.replace("\\", "/")
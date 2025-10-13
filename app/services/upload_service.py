import os
from werkzeug.utils import secure_filename
from datetime import datetime

class UploadService:
    def __init__(self, root_dir: str):
        self.root = root_dir

    def save_image(self, owner_id: int, file_storage) -> str:
        """
        ตรวจชนิด/ขนาดไฟล์รูป, ตั้งชื่อไฟล์ปลอดภัย, บันทึกลง uploads/<owner_id>/images/, และคืนค่า relative path
        """
        owner_dir_for_saving = os.path.join(self.root, str(owner_id), "images")
        os.makedirs(owner_dir_for_saving, exist_ok=True)
        
        filename = secure_filename(file_storage.filename or "image")
        full_save_path = os.path.join(owner_dir_for_saving, filename)
        file_storage.save(full_save_path)
        
        relative_path_for_url = os.path.join("uploads", str(owner_id), "images", filename)
        
        return relative_path_for_url.replace("\\", "/")

    # --- vvv ส่วนที่เพิ่มเข้ามาใหม่ vvv ---
    def save_document(self, owner_id: int, file_storage) -> str:
        """
        บันทึกเอกสาร (PDF), สร้างชื่อไฟล์ที่ปลอดภัย, เก็บไว้ใน uploads/<owner_id>/documents/,
        และคืนค่า relative path สำหรับเก็บลงฐานข้อมูล
        """
        owner_dir_for_saving = os.path.join(self.root, str(owner_id), "documents")
        os.makedirs(owner_dir_for_saving, exist_ok=True)
        
        filename = secure_filename(file_storage.filename or "document.pdf")
        # เพิ่ม timestamp เพื่อป้องกันชื่อไฟล์ซ้ำ
        unique_filename = f"{int(datetime.utcnow().timestamp())}_{filename}"
        full_save_path = os.path.join(owner_dir_for_saving, unique_filename)
        file_storage.save(full_save_path)
        
        relative_path_for_url = os.path.join("uploads", str(owner_id), "documents", unique_filename)
        
        return relative_path_for_url.replace("\\", "/")
    # --- ^^^ สิ้นสุดส่วนที่เพิ่ม ^^^ ---
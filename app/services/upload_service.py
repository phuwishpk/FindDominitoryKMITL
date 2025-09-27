import os
from werkzeug.utils import secure_filename

class UploadService:
    def __init__(self, root_dir: str):
        self.root = root_dir

    def save_image(self, owner_id: int, file_storage) -> str:
        """
        ตรวจชนิด/ขนาดไฟล์รูป, ตั้งชื่อไฟล์ปลอดภัย, บันทึกลง uploads/<owner_id>/images/, และคืนค่า relative path
        """
        owner_dir = os.path.join(self.root, str(owner_id), "images")
        os.makedirs(owner_dir, exist_ok=True)
        filename = secure_filename(file_storage.filename or "image")
        path = os.path.join(owner_dir, filename)
        file_storage.save(path)
        return path.replace("\\", "/")
import os, imghdr
from werkzeug.utils import secure_filename


ALLOWED_IMG = {"jpg","jpeg","png","webp"}


class UploadService:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir


    def save_image(self, owner_id: int, file_storage) -> str:
        filename = secure_filename(file_storage.filename)
        ext = filename.rsplit('.', 1)[-1].lower()
        if ext not in ALLOWED_IMG:
         raise ValueError("Invalid image type")
        target = os.path.join(self.base_dir, str(owner_id), "images")
        os.makedirs(target, exist_ok=True)
        path = os.path.join(target, filename)
        file_storage.save(path)
        if imghdr.what(path) is None:
         os.remove(path)
        raise ValueError("File is not an image")
        return path


    def save_pdf(self, owner_id: int, file_storage) -> str:
        filename = secure_filename(file_storage.filename)
        if not filename.lower().endswith('.pdf'):
         raise ValueError('Only PDF allowed')
        target = os.path.join(self.base_dir, str(owner_id), 'docs')
        os.makedirs(target, exist_ok=True)
        path = os.path.join(target, filename)
        file_storage.save(path)
        return path
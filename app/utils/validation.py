# app/utils/validation.py

import re
from werkzeug.datastructures import FileStorage
# เพิ่มการ import ที่จำเป็น
from wtforms.validators import ValidationError

_CID_RE = re.compile(r"^\d{13}$")

def is_valid_citizen_id(cid: str) -> bool:
    if not cid or not _CID_RE.match(cid):
        return False
    digits = [int(c) for c in cid]
    s = sum(d * w for d, w in zip(digits[:12], range(13, 1, -1)))
    check = (11 - (s % 11)) % 10
    return check == digits[12]

ALLOWED_IMG = {"jpg", "jpeg", "png", "webp"}

# --- ไม่ได้ใช้แล้ว สามารถลบออกได้ ---
# class FileTypeError(ValueError):
#     ...
# class FileSizeError(ValueError):
#     ...

def validate_image_file(fs: FileStorage, max_mb: int = 3):
    filename = (fs.filename or "").lower()
    if "." not in filename:
        raise ValidationError("ชื่อไฟล์ไม่ถูกต้อง")
    ext = filename.rsplit(".", 1)[-1]
    if ext not in ALLOWED_IMG:
        raise ValidationError("อนุญาตเฉพาะไฟล์รูปภาพ (jpg, jpeg, png, webp) เท่านั้น")
    fs.stream.seek(0, 2)
    size = fs.stream.tell()
    fs.stream.seek(0)
    if size > max_mb * 1024 * 1024:
        raise ValidationError(f"ขนาดไฟล์รูปภาพต้องไม่เกิน {max_mb}MB")

# --- vvv ส่วนที่แก้ไข vvv ---
def validate_pdf_file(fs: FileStorage, max_mb: int = 10):
    """
    ตรวจสอบไฟล์ว่าเป็น PDF และขนาดไม่เกินที่กำหนด
    หากไม่ถูกต้องจะ raise ValidationError พร้อมข้อความภาษาไทย
    """
    filename = (fs.filename or "").lower()
    # ตรวจสอบว่าลงท้ายด้วย .pdf หรือไม่
    if not filename.endswith(".pdf"):
        raise ValidationError("ไฟล์ที่อัปโหลดต้องเป็นชนิด PDF เท่านั้น")

    # ตรวจสอบขนาดไฟล์ (เหมือนเดิม)
    fs.stream.seek(0, 2)
    size = fs.stream.tell()
    fs.stream.seek(0)
    if size > max_mb * 1024 * 1024:
        raise ValidationError(f"ขนาดไฟล์ PDF ต้องไม่เกิน {max_mb}MB")
# --- ^^^ สิ้นสุดส่วนที่แก้ไข ^^^ ---
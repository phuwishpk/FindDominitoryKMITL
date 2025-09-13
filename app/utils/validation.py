import re
from werkzeug.datastructures import FileStorage

_CID_RE = re.compile(r"^\d{13}$")

def is_valid_citizen_id(cid: str) -> bool:
    if not cid or not _CID_RE.match(cid):
        return False
    digits = [int(c) for c in cid]
    s = sum(d * w for d, w in zip(digits[:12], range(13, 1, -1)))
    check = (11 - (s % 11)) % 10
    return check == digits[12]

ALLOWED_IMG = {"jpg", "jpeg", "png", "webp"}

class FileTypeError(ValueError):
    ...

class FileSizeError(ValueError):
    ...

def validate_image_file(fs: FileStorage, max_mb: int = 3):
    filename = (fs.filename or "").lower()
    if "." not in filename:
        raise FileTypeError("Invalid filename")
    ext = filename.rsplit(".", 1)[-1]
    if ext not in ALLOWED_IMG:
        raise FileTypeError("Invalid image type")
    fs.stream.seek(0, 2)
    size = fs.stream.tell()
    fs.stream.seek(0)
    if size > max_mb * 1024 * 1024:
        raise FileSizeError("Image too large")

def validate_pdf_file(fs: FileStorage, max_mb: int = 10):
    filename = (fs.filename or "").lower()
    if not filename.endswith(".pdf"):
        raise FileTypeError("Only PDF allowed")
    fs.stream.seek(0, 2)
    size = fs.stream.tell()
    fs.stream.seek(0)
    if size > max_mb * 1024 * 1024:
        raise FileSizeError("PDF too large")

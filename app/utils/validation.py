import re
from werkzeug.datastructures import FileStorage

class CitizenIDValidator:
    """
    A class to validate Thai citizen identification numbers.
    """
    _CID_RE = re.compile(r"^\d{13}$")

    def is_valid(self, cid: str) -> bool:
        """
        Validates the format and checksum of a 13-digit Thai citizen ID.

        Args:
            cid: The citizen ID string to validate.

        Returns:
            True if the citizen ID is valid, False otherwise.
        """
        if not cid or not self._CID_RE.match(cid):
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

class FileValidator:
    """
    A class to validate file uploads, checking for type and size.
    """
    def validate_image_file(self, fs: FileStorage, max_mb: int = 3):
        """
        Validates an image file based on allowed extensions and file size.

        Args:
            fs: The FileStorage object from Werkzeug.
            max_mb: The maximum allowed file size in megabytes.

        Raises:
            FileTypeError: If the file type is not allowed.
            FileSizeError: If the file size exceeds the maximum limit.
        """
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

    def validate_pdf_file(self, fs: FileStorage, max_mb: int = 10):
        """
        Validates a PDF file, checking for the correct extension and file size.

        Args:
            fs: The FileStorage object from Werkzeug.
            max_mb: The maximum allowed file size in megabytes.

        Raises:
            FileTypeError: If the file is not a PDF.
            FileSizeError: If the file size exceeds the maximum limit.
        """
        filename = (fs.filename or "").lower()
        if not filename.endswith(".pdf"):
            raise FileTypeError("Only PDF allowed")
        fs.stream.seek(0, 2)
        size = fs.stream.tell()
        fs.stream.seek(0)
        if size > max_mb * 1024 * 1024:
            raise FileSizeError("PDF too large")

# Instantiate validators for easy import and use
citizen_id_validator = CitizenIDValidator()
file_validator = FileValidator()
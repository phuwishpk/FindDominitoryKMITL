# tests/test_validation_utils.py

from app.utils.validation import is_valid_citizen_id

def test_valid_citizen_id():
    """
    ทดสอบ: ฟังก์ชัน is_valid_citizen_id ควรคืนค่า True
    เมื่อได้รับเลขบัตรประชาชนที่ถูกต้อง
    """
    valid_id = "1101700203451" # ตัวอย่างเลขบัตรที่ถูกต้อง
    assert is_valid_citizen_id(valid_id) is True

def test_invalid_citizen_id_checksum():
    """
    ทดสอบ: ฟังก์ชัน is_valid_citizen_id ควรคืนค่า False
    เมื่อได้รับเลขบัตรที่ checksum ไม่ถูกต้อง
    """
    invalid_id = "1101700203452" # ตัวเลขหลักสุดท้ายผิด
    assert is_valid_citizen_id(invalid_id) is False

def test_invalid_citizen_id_length():
    """
    ทดสอบ: ฟังก์ชัน is_valid_citizen_id ควรคืนค่า False
    เมื่อได้รับเลขบัตรที่ความยาวไม่ครบ 13 หลัก
    """
    short_id = "12345"
    assert is_valid_citizen_id(short_id) is False
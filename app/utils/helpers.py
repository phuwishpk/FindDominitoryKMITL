from datetime import datetime
import pytz
import json
# --- vvv ส่วนที่เพิ่มเข้ามาใหม่ vvv ---
from flask import session
import random
# --- ^^^ สิ้นสุดส่วนที่เพิ่ม ^^^ ---


def format_as_bangkok_time(utc_dt):
    """
    ฟิลเตอร์สำหรับ Jinja2 เพื่อแปลง datetime object ที่เป็น UTC
    ให้เป็นโซนเวลาของกรุงเทพฯ (ICT) และจัดรูปแบบให้สวยงาม
    """
    if not isinstance(utc_dt, datetime):
        return utc_dt # ถ้าข้อมูลไม่ใช่ datetime ให้ส่งค่าเดิมกลับไป

    # กำหนดโซนเวลาของกรุงเทพฯ (Indochina Time, UTC+7)
    bangkok_tz = pytz.timezone("Asia/Bangkok")

    # แปลงเวลา UTC จากฐานข้อมูลให้เป็นเวลาของกรุงเทพฯ
    bangkok_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(bangkok_tz)

    # จัดรูปแบบการแสดงผล
    return bangkok_dt.strftime('%d/%m/%Y %H:%M:%S')

def from_json_string(json_string):
    """
    ฟิลเตอร์สำหรับ Jinja2 เพื่อแปลง JSON string เป็น Python object
    """
    if json_string:
        try:
            return json.loads(json_string)
        except (json.JSONDecodeError, TypeError):
            # ในกรณีที่ข้อมูลใน meta ไม่ใช่ JSON string ที่ถูกต้อง
            return None
    return None

# --- vvv ส่วนที่เพิ่มเข้ามาใหม่ vvv ---
def get_anonymous_name():
    """
    สร้างหรือดึงชื่อสำหรับผู้ใช้ anonymous จาก session
    """
    if 'anonymous_name' not in session:
        # รายชื่อคำคุณศัพท์และคำนามสำหรับสร้างชื่อสุ่ม
        adjectives = ["นักสำรวจ", "นักชิม", "นักเดินทาง", "ผู้รักสงบ", "ผู้ชื่นชอบ", "นักผจญภัย"]
        nouns = ["ปริศนา", "นิรนาม", "ลึกลับ", "สายลม", "แห่งรั้วนนทรี"]
        
        # สุ่มชื่อและตัวเลข
        random_name = f"{random.choice(adjectives)} {random.choice(nouns)} #{random.randint(1000, 9999)}"
        session['anonymous_name'] = random_name
    return session['anonymous_name']
# --- ^^^ สิ้นสุดส่วนที่เพิ่ม ^^^ ---
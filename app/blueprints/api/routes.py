"""
ไฟล์สำหรับกำหนด Routes ของ API Blueprint
ในที่นี้เราใช้ Flask-RESTful เพื่อสร้าง API ในรูปแบบ OOP
"""

from flask import Blueprint, jsonify
from flask_restful import Api, Resource

# สร้าง Blueprint สำหรับ API
# A Blueprint is an object that allows defining application functions without requiring an application object ahead of time.
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# สร้าง Instance ของ Api จาก Flask-RESTful โดยผูกกับ Blueprint
api = Api(api_bp)

class HealthCheckResource(Resource):
    """
    Resource สำหรับตรวจสอบสถานะของระบบ (Health Check)
    สืบทอดมาจาก Resource ของ Flask-RESTful
    """
    def get(self):
        """
        จัดการกับ HTTP GET request
        คืนค่าสถานะของแอปพลิเคชันในรูปแบบ JSON
        """
        # โดยปกติข้อมูล version จะถูกดึงมาจากไฟล์ config หรือตัวแปรสภาพแวดล้อม
        app_version = "1.0.0" 
        
        response_data = {
            "status": "ok",
            "version": app_version
        }
        # Flask-RESTful จะแปลง dict เป็น JSON response โดยอัตโนมัติ
        return response_data

# เพิ่ม Resource เข้าไปใน API พร้อมกำหนด endpoint
# การเรียกมาที่ /api/v1/health จะถูกส่งมาที่ HealthCheckResource
api.add_resource(HealthCheckResource, '/health')

# ฟังก์ชันนี้สามารถถูก import และ register ในไฟล์สร้างแอปหลัก
def init_app(app):
    """
    ฟังก์ชันสำหรับลงทะเบียน Blueprint นี้กับ Flask app instance
    """
    app.register_blueprint(api_bp)

# File: app/__init__.py
from flask import Flask, send_from_directory
# 🛠️ แก้ไข: ตรวจสอบให้แน่ใจว่า import 'babel' ถูกต้อง
from .extensions import db, migrate, login_manager, babel, limiter, csrf
from .config import Config

from .blueprints.public import bp as public_bp
from .blueprints.owner import bp as owner_bp
from .blueprints.admin import bp as admin_bp
from .blueprints.auth import bp as auth_bp
from .blueprints.api import bp as api_bp

# ⬇️ [app/repositories/sqlalchemy] นำเข้า Repositories
from .repositories.sqlalchemy.user_repo_sql import SqlUserRepo
from .repositories.sqlalchemy.property_repo_sql import SqlPropertyRepo
from .repositories.sqlalchemy.approval_repo_sql import SqlApprovalRepo

# ⬇️ [app/services] นำเข้า Services
from .services.auth_service import AuthService
from .services.property_service import PropertyService
from .services.search_service import SearchService
from .services.approval_service import ApprovalService
from .services.upload_service import UploadService
from .services.dashboard_service import DashboardService # 🛠️ เพิ่ม: DashboardService

# 🛠️ [app/forms/upload.py] ต้อง Import EmptyForm เพื่อใช้ใน Context Processor
from .forms.upload import EmptyForm 

def register_dependencies(app: Flask):
    container = {}
    container["user_repo"] = SqlUserRepo()
    container["property_repo"] = SqlPropertyRepo()
    container["approval_repo"] = SqlApprovalRepo()
    
    # 🛠️ [app/services/upload_service.py] สร้าง UploadService ก่อน
    container["upload_service"] = UploadService(app.config.get("UPLOAD_FOLDER", "uploads"))

    # 🛠️ [app/services/auth_service.py] ส่ง upload_service เข้าไปใน AuthService
    container["auth_service"] = AuthService(
        user_repo=container["user_repo"],
        upload_service=container["upload_service"],
    )
    
    container["property_service"] = PropertyService(container["property_repo"])
    container["search_service"] = SearchService(container["property_repo"])
    
    # 🛠️ แก้ไข: ApprovalService ต้องรับ approval_repo และ property_repo เป็น argument
    container["approval_service"] = ApprovalService(
        container["approval_repo"],
        container["property_repo"]
    )
    
    # 🛠️ เพิ่ม: DashboardService ต้องรับ Repositories ที่เกี่ยวข้อง
    container["dashboard_service"] = DashboardService(
        user_repo=container["user_repo"],
        property_repo=container["property_repo"],
        approval_repo=container["approval_repo"],
    )
    
    if not hasattr(app, "extensions"):
        app.extensions = {}
    app.extensions["container"] = container

def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    babel.init_app(app) # 🛠️ ใช้ babel ที่ import มา
    limiter.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        register_dependencies(app)

    # ⬇️ [app/blueprints] ลงทะเบียน Blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(owner_bp, url_prefix="/owner")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(api_bp, url_prefix="/api")
    
    # 🛠️ [app/__init__.py] เพิ่ม Context Processor เพื่อแก้ปัญหา UndefinedError
    @app.context_processor
    def inject_forms():
        """ส่ง empty_form เข้าสู่ทุก Template Context (ใช้สำหรับ csrf_token ในปุ่มลบต่างๆ)"""
        # ⬇️ [app/forms/upload.py]
        return dict(empty_form=EmptyForm())
    
    # 🛠️ [app/__init__.py] เพิ่ม: Endpoint สำหรับให้บริการไฟล์อัปโหลด
    @app.route("/uploads/<path:filename>")
    def serve_uploads(filename):
        return send_from_directory(
            app.config["UPLOAD_FOLDER"],
            filename,
            as_attachment=False,
        )

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.cli.command("seed_amenities")
    def seed_amenities():
        # ⬇️ [app/models/property.py]
        from app.models.property import Amenity
        from app.extensions import db
        data = [
            ("pet","อนุญาตสัตว์เลี้ยง","Pets allowed"),
            ("ac","เครื่องปรับอากาศ","Air conditioning"),
            ("guard","รปภ.","Security guard"),
            ("cctv","กล้อง CCTV","CCTV"),
            ("fridge","ตู้เย็น","Refrigerator"),
            ("bed","เตียง","Bed"),
            ("heater","เครื่องทำน้ำอุ่น","Water heater"),
            ("internet","อินเทอร์เน็ต","Internet"),
            ("tv","ทีวี","TV"),
            ("sofa","โซฟา","Sofa"),
            ("wardrobe","ตู้เสื้อผ้า","Wardrobe"),
            ("desk","โต๊ะทำงาน","Desk"),
        ]
        for code, th, en in data:
            if not Amenity.query.filter_by(code=code).first():
                db.session.add(Amenity(code=code, label_th=th, label_en=en))
        db.session.commit()
        print("Seeded amenities ✅")

    @app.cli.command("seed_sample")
    def seed_sample():
        # ⬇️ [app/models/user.py], [app/models/property.py]
        from app.models.user import Owner, Admin
        from app.models.property import Property
        from app.extensions import db
        from werkzeug.security import generate_password_hash
        
        # Seed Owner
        if not Owner.query.filter_by(email="owner@example.com").first():
            o = Owner(full_name_th="เจ้าของตัวอย่าง", citizen_id="1101700203451",
                      email="owner@example.com", password_hash=generate_password_hash("password"))
            db.session.add(o); db.session.commit()
            
            # Seed Property
            p = Property(owner_id=o.id, dorm_name="ตัวอย่างหอพัก", room_type="studio",
                         rent_price=6500, lat=13.7563, lng=100.5018,
                         workflow_status="approved")
            db.session.add(p); db.session.commit()
            
        # Seed Admin
        if not Admin.query.filter_by(username="admin").first():
            a = Admin(username="admin", password_hash=generate_password_hash("admin"), display_name="Administrator")
            db.session.add(a); db.session.commit()
            
        print("Seeded sample data ✅")

    return app

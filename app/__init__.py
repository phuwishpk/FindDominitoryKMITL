import os
from flask import Flask, g
from flask_wtf import CSRFProtect

from .extensions import db, migrate, login_manager, babel, limiter, csrf
from .config import Config

# Blueprints
from .blueprints.public import bp as public_bp
from .blueprints.owner import bp as owner_bp
from .blueprints.admin import bp as admin_bp
from .blueprints.auth import bp as auth_bp
from .blueprints.api import bp as api_bp

# Repositories
from .repositories.sqlalchemy.user_repo_sql import SqlUserRepo
from .repositories.sqlalchemy.property_repo_sql import SqlPropertyRepo
from .repositories.sqlalchemy.approval_repo_sql import SqlApprovalRepo
from .repositories.sqlalchemy.review_repo_sql import SqlReviewRepo

# Services
from .services.auth_service import AuthService
from .services.property_service import PropertyService
from .services.search_service import SearchService
from .services.approval_service import ApprovalService
from .services.upload_service import UploadService
from .services.location_service import LocationService
from .services.dashboard_service import DashboardService
from .services.review_service import ReviewService

def register_dependencies(app: Flask):
    """
    Dependency injection container.
    """
    container = {}
    
    # Repositories
    container["user_repo"] = SqlUserRepo()
    container["property_repo"] = SqlPropertyRepo()
    container["approval_repo"] = SqlApprovalRepo()
    container["review_repo"] = SqlReviewRepo()

    # Services (services with no dependencies first)
    container["upload_service"] = UploadService(app.config.get("UPLOAD_FOLDER", "uploads"))
    container["location_service"] = LocationService()
    container["approval_service"] = ApprovalService(container["approval_repo"], container["property_repo"])
    container["auth_service"] = AuthService(container["user_repo"])
    
    # --- บรรทัดที่แก้ไข ---
    # ส่ง upload_service และ location_service ไปให้ PropertyService
    container["property_service"] = PropertyService(container["property_repo"], container["upload_service"], container["location_service"])
    # --- สิ้นสุดการแก้ไข ---

    container["search_service"] = SearchService(container["property_repo"])
    container["dashboard_service"] = DashboardService(container["property_repo"])
    container["review_service"] = ReviewService(container["review_repo"])
    
    if not hasattr(app, "extensions"):
        app.extensions = {}
    app.extensions["container"] = container

def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    babel.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        register_dependencies(app)

    # Register blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(owner_bp, url_prefix="/owner")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(api_bp, url_prefix="/api")
    
    @app.before_request
    def before_request():
        # ตั้งค่า empty_form สำหรับใช้กับฟอร์ม logout ใน navbar
        from app.forms.auth import EmptyForm
        g.empty_form = EmptyForm()

    @app.context_processor
    def inject_empty_form():
        # ทำให้ empty_form ใช้ได้ใน template ทั้งหมด
        return dict(empty_form=g.empty_form)

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.cli.command("seed_amenities")
    def seed_amenities():
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
        from app.models.user import Owner, Admin
        from app.models.property import Property
        from app.extensions import db
        from werkzeug.security import generate_password_hash
        
        location_pin_data = {"type": "Point", "coordinates": [100.7758, 13.7292]}

        if not Owner.query.filter_by(email="owner@example.com").first():
            o = Owner(full_name_th="เจ้าของตัวอย่าง", citizen_id="1101700203451",
                      email="owner@example.com", password_hash=generate_password_hash("password"))
            db.session.add(o); db.session.commit()
            
            p = Property(owner_id=o.id, dorm_name="ตัวอย่างหอพัก", room_type="studio",
                         rent_price=6500, 
                         location_pin=location_pin_data, 
                         workflow_status=Property.WORKFLOW_APPROVED)
            db.session.add(p); db.session.commit()
            
        if not Admin.query.filter_by(username="admin").first():
            a = Admin(username="admin", password_hash=generate_password_hash("admin"), display_name="Administrator")
            db.session.add(a); db.session.commit()
        print("Seeded sample data ✅")

    return app
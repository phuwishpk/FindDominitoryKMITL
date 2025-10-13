# app/__init__.py
from flask import Flask, send_from_directory
from .extensions import db, migrate, login_manager, babel_ext, limiter, csrf
from .config import Config
from .utils.helpers import format_as_bangkok_time, from_json_string
from .forms.upload import EmptyForm  # safe

def register_dependencies(app: Flask):
    # ⬇️ import ภายในฟังก์ชัน เพื่อตัดวงจรอิมพอร์ต
    from .repositories.sqlalchemy.user_repo_sql import SqlUserRepo
    from .repositories.sqlalchemy.property_repo_sql import SqlPropertyRepo
    from .repositories.sqlalchemy.approval_repo_sql import SqlApprovalRepo

    from .services.auth_service import AuthService
    from .services.property_service import PropertyService
    from .services.search_service import SearchService
    from .services.approval_service import ApprovalService
    from .services.upload_service import UploadService
    from .services.dashboard_service import DashboardService

    container = {}
    container["user_repo"] = SqlUserRepo()
    container["property_repo"] = SqlPropertyRepo()
    container["approval_repo"] = SqlApprovalRepo()
    container["upload_service"] = UploadService(app.config.get("UPLOAD_FOLDER", "uploads"))

    container["auth_service"] = AuthService(
        user_repo=container["user_repo"],
        upload_service=container["upload_service"],
    )
    container["property_service"] = PropertyService(container["property_repo"])
    container["search_service"] = SearchService(container["property_repo"])
    container["approval_service"] = ApprovalService(
        container["approval_repo"], container["property_repo"]
    )
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

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    babel_ext.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)

    # jinja filters
    app.jinja_env.filters["to_bkk_time"] = format_as_bangkok_time
    app.jinja_env.filters["fromjson"] = from_json_string

    # DI container
    register_dependencies(app)

    # ⬇️ import blueprints ภายใน create_app
    from .blueprints.public import bp as public_bp
    from .blueprints.owner import bp as owner_bp
    from .blueprints.admin import bp as admin_bp
    from .blueprints.auth import bp as auth_bp
    from .blueprints.api import bp as api_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(owner_bp, url_prefix="/owner")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.context_processor
    def inject_forms():
        return dict(empty_form=EmptyForm())

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
        from app.models.property import Amenity
        from app.extensions import db

        data = [
            ("pet", "อนุญาตสัตว์เลี้ยง", "Pets allowed"),
            ("ac", "เครื่องปรับอากาศ", "Air conditioning"),
            ("guard", "รปภ.", "Security guard"),
            ("cctv", "กล้อง CCTV", "CCTV"),
            ("fridge", "ตู้เย็น", "Refrigerator"),
            ("bed", "เตียง", "Bed"),
            ("heater", "เครื่องทำน้ำอุ่น", "Water heater"),
            ("internet", "อินเทอร์เน็ต", "Internet"),
            ("tv", "ทีวี", "TV"),
            ("sofa", "โซฟา", "Sofa"),
            ("wardrobe", "ตู้เสื้อผ้า", "Wardrobe"),
            ("desk", "โต๊ะทำงาน", "Desk"),
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
            o = Owner(
                full_name_th="เจ้าของตัวอย่าง",
                citizen_id="1101700203451",
                email="owner@example.com",
                password_hash=generate_password_hash("password"),
            )
            db.session.add(o)
            db.session.commit()

            # 🔧 เปลี่ยน dorm_name -> title และเติมฟิลด์ให้ตรงกับโมเดล
            p = Property(
                owner_id=o.id,
                title="ตัวอย่างหอพัก",
                property_type="dorm",
                room_type="studio",
                price=6500,
                rent_price=6500,
                location_pin=location_pin_data,
                workflow_status=Property.WORKFLOW_APPROVED,
            )
            db.session.add(p)
            db.session.commit()

        if not Admin.query.filter_by(username="admin").first():
            a = Admin(
                username="admin",
                password_hash=generate_password_hash("admin"),
                display_name="Administrator",
            )
            db.session.add(a)
            db.session.commit()

        print("Seeded sample data ✅")

    return app

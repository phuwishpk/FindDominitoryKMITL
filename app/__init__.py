import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

# --- ส่วนของการสร้าง Application และตั้งค่า ---

# สร้าง instance ของ SQLAlchemy แต่ยังไม่ผูกกับ app
db = SQLAlchemy()

def create_app(config_object="app.config.Config"):
    """
    Application Factory Pattern
    """
    app = Flask(__name__)
    app.config.from_object(config_object)

    # ผูก extensions เข้ากับ app
    db.init_app(app)

    from .extensions import login_manager, principal
    login_manager.init_app(app)
    principal.init_app(app)
    login_manager.login_view = 'auth.login' # ตั้งค่าหน้า login สำหรับ redirect

    with app.app_context():
        # สร้าง Dependency Injection Container
        register_dependencies(app)

        # Import models เพื่อให้ SQLAlchemy สร้างตารางได้
        from . import models
        db.create_all()

        # Register Blueprints (ถ้ามี)
        # from .routes import main_bp
        # app.register_blueprint(main_bp)

        # Register CLI commands
        register_cli_commands(app)

    return app

def register_dependencies(app) -> None:
    """
    ผูก Dependency Injection (DI):
    สร้าง instances ของ Repositories และ Services แล้วเก็บไว้ใน app.config
    เพื่อให้สามารถเรียกใช้ได้จากส่วนต่างๆ ของแอปพลิเคชัน
    """
    from .repositories import AdminRepository, OwnerRepository, PropertyRepository, AmenityRepository
    from .services import AuthService

    # สร้าง instances ของ Repositories โดยส่ง db.session เข้าไป
    admin_repo = AdminRepository(db.session)
    owner_repo = OwnerRepository(db.session)
    prop_repo = PropertyRepository(db.session)
    amenity_repo = AmenityRepository(db.session)

    # สร้าง instances ของ Services โดยส่ง repositories ที่จำเป็นเข้าไป
    auth_service = AuthService(owner_repo=owner_repo, admin_repo=admin_repo)

    # เก็บ instances ไว้ใน container (ใช้ dict ใน app.config)
    app.config["container"] = {
        "admin_repository": admin_repo,
        "owner_repository": owner_repo,
        "property_repository": prop_repo,
        "amenity_repository": amenity_repo,
        "auth_service": auth_service,
    }
    print("Dependencies registered.")

def register_cli_commands(app):
    """
    ลงทะเบียนคำสั่งสำหรับ Flask CLI
    """
    @app.cli.command("seed-amenities")
    def seed_amenities():
        """เติมข้อมูล master data (amenities)"""
        from .models import Amenity
        container = app.config["container"]
        amenity_repo = container["amenity_repository"]

        if amenity_repo.get_all():
            print("Amenities already exist. Skipping.")
            return

        amenities_to_add = [
            Amenity(name="Wi-Fi"),
            Amenity(name="Air Conditioning"),
            Amenity(name="Swimming Pool"),
            Amenity(name="Parking"),
            Amenity(name="Gym"),
        ]
        for amenity in amenities_to_add:
            amenity_repo.add(amenity)

        print(f"Added {len(amenities_to_add)} amenities to the database.")


    @app.cli.command("seed-sample")
    def seed_sample():
        """เติมข้อมูลตัวอย่าง (admin, owner, property)"""
        from .models import Admin, Owner, Property
        container = app.config["container"]
        auth_service = container["auth_service"]
        owner_repo = container["owner_repository"]
        admin_repo = container["admin_repository"]
        prop_repo = container["property_repository"]

        # 1. สร้าง Admin
        if not admin_repo.find_by_username("admin"):
            admin_user = Admin(
                username="admin",
                password_hash=generate_password_hash("password123")
            )
            admin_repo.add(admin_user)
            print("Admin user 'admin' created.")
        else:
            print("Admin user 'admin' already exists.")

        # 2. สร้าง Owner
        if not owner_repo.find_by_email("owner@example.com"):
            owner_data = {
                "email": "owner@example.com",
                "password": "password123",
                "first_name": "John",
                "last_name": "Doe",
                "id_card_pdf_path": "/static/docs/sample_id.pdf"
            }
            new_owner = auth_service.register_owner(owner_data)
            print(f"Owner '{new_owner.email}' created.")

            # 3. สร้าง Property
            if not prop_repo.find_by_name("Sample Villa"):
                sample_property = Property(
                    name="Sample Villa",
                    address="123 Main St, Bangkok",
                    owner_id=new_owner.id
                )
                prop_repo.add(sample_property)
                print(f"Property '{sample_property.name}' created for owner '{new_owner.email}'.")
        else:
            print("Sample owner and property already exist.")

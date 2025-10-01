import click
from flask import Flask, current_app
from dependency_injector import containers, providers

# from . import models, repositories # Import ที่จำเป็น
from .services.auth_service import AuthService
from .extensions import db, migrate, bcrypt, login_manager

class Container(containers.DeclarativeContainer):
    """
    Dependency Injection Container
    - ผูก (wire) dependencies ต่างๆ เข้าด้วยกัน
    - ทำให้สามารถสลับ implementation ได้ง่าย (เช่น สลับไปใช้ MockRepository ตอนทดสอบ)
    """
    # กำหนด config ที่จะรับเข้ามา
    config = providers.Configuration()

    # Database session provider
    db_session = providers.Singleton(lambda: db.session)

    # --- Repositories ---
    # Factory จะสร้าง instance ใหม่ทุกครั้งที่เรียกใช้
    owner_repository = providers.Factory(
        repositories.OwnerRepository,
        session_factory=db_session
    )
    admin_repository = providers.Factory(
        repositories.AdminRepository,
        session_factory=db_session
    )
    amenity_repository = providers.Factory(
        repositories.AmenityRepository,
        session_factory=db_session
    )
    # ... เพิ่ม repositories อื่นๆ ตามต้องการ

    # --- Services ---
    # AuthService จะถูกสร้างขึ้นโดยรับ repository instances ที่ DI container สร้างให้
    auth_service = providers.Factory(
        AuthService,
        owner_repository=owner_repository,
        admin_repository=admin_repository,
    )

def register_dependencies(app: Flask):
    """
    สร้างและผูก DI container เข้ากับ application
    """
    container = Container()
    app.container = container
    # ทำให้ container สามารถเข้าถึง config ของ app ได้
    container.config.from_dict(app.config)
    # ทำให้ DI container สามารถ inject dependency ไปยัง route/blueprint ได้
    # container.wire(modules=[__name__, ".routes.auth", ".routes.properties"])


def register_cli_commands(app: Flask):
    """
    ลงทะเบียนคำสั่งสำหรับ Command-Line Interface (CLI)
    """
    @app.cli.command("seed-amenities")
    def seed_amenities_command():
        """เติมข้อมูล master data (amenities)"""
        with app.app_context():
            # เข้าถึง repository ผ่าน DI container ของ app
            amenity_repo = current_app.container.amenity_repository()
            
            amenities_to_add = ["สระว่ายน้ำ", "ฟิตเนส", "ที่จอดรถ", "Wi-Fi"]
            for name in amenities_to_add:
                if not amenity_repo.find_by_name(name):
                    amenity_repo.create(name=name)
            
            click.echo("Amenities have been seeded.")

    @app.cli.command("seed-sample")
    def seed_sample_command():
        """เติมข้อมูลตัวอย่าง (admin/owner/property)"""
        with app.app_context():
            # เข้าถึง service ผ่าน DI container ของ app
            auth_service = current_app.container.auth_service()
            
            # สร้าง Admin ตัวอย่าง
            admin_repo = current_app.container.admin_repository()
            if not admin_repo.find_by_username("admin"):
                hashed_pass = bcrypt.generate_password_hash("password").decode('utf-8')
                admin_repo.create(username="admin", password_hash=hashed_pass)
                click.echo("Sample admin created.")

            # สร้าง Owner ตัวอย่าง
            owner_repo = current_app.container.owner_repository()
            if not owner_repo.find_by_email("owner@example.com"):
                hashed_pass = bcrypt.generate_password_hash("password").decode('utf-8')
                owner_repo.create(
                    email="owner@example.com",
                    password_hash=hashed_pass,
                    first_name="Sample",
                    last_name="Owner"
                )
                click.echo("Sample owner created.")
        
        click.echo("Sample data has been seeded.")


def create_app(config_object="app.config.Config"):
    """
    Application Factory Pattern
    """
    app = Flask(__name__)
    app.config.from_object(config_object)

    # --- Initialize Extensions ---
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # --- Register Dependencies ---
    register_dependencies(app)

    # --- Register CLI Commands ---
    register_cli_commands(app)

    # --- Register Blueprints ---
    # from .routes import auth_bp, property_bp
    # app.register_blueprint(auth_bp, url_prefix='/auth')
    # app.register_blueprint(property_bp)

    return app

import click
from flask import Flask, current_app, send_from_directory
from dependency_injector import containers, providers

from .services.auth_service import AuthService
from .extensions import db, migrate, bcrypt, login_manager

# --- Repositories imports (ตัวอย่าง) ---
# from . import repositories

class Container(containers.DeclarativeContainer):
    """
    Dependency Injection Container
    """
    config = providers.Configuration()
    db_session = providers.Singleton(lambda: db.session)

    # Repositories
    owner_repository = providers.Factory(
        lambda: repositories.OwnerRepository(session_factory=db_session())
    )
    admin_repository = providers.Factory(
        lambda: repositories.AdminRepository(session_factory=db_session())
    )
    amenity_repository = providers.Factory(
        lambda: repositories.AmenityRepository(session_factory=db_session())
    )

    # Services
    auth_service = providers.Factory(
        AuthService,
        owner_repository=owner_repository,
        admin_repository=admin_repository,
    )

def register_dependencies(app: Flask):
    """
    ผูก DI container เข้ากับ Flask app
    """
    container = Container()
    app.container = container
    container.config.from_dict(app.config)
    # container.wire(modules=[__name__])

def register_cli_commands(app: Flask):
    """
    ลงทะเบียน CLI commands
    """
    @app.cli.command("seed-amenities")
    def seed_amenities_command():
        """เติมข้อมูล master data (amenities)"""
        with app.app_context():
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
            auth_service = current_app.container.auth_service()
            owner_repo = current_app.container.owner_repository()
            admin_repo = current_app.container.admin_repository()

            # สร้าง Admin ตัวอย่าง
            if not admin_repo.find_by_username("admin"):
                hashed_pass = bcrypt.generate_password_hash("password").decode('utf-8')
                admin_repo.create(username="admin", password_hash=hashed_pass)
                click.echo("Sample admin created.")

            # สร้าง Owner ตัวอย่าง
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

def create_app(config_object="app.config.Config") -> Flask:
    """
    Application Factory Pattern
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)

    # --- Initialize Extensions ---
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    # babel.init_app(app)
    # limiter.init_app(app)
    # csrf.init_app(app)

    # --- Register Dependencies & CLI ---
    register_dependencies(app)
    register_cli_commands(app)

    # --- Blueprints ---
    # from .routes import auth_bp, owner_bp, admin_bp, public_bp, api_bp
    # app.register_blueprint(auth_bp, url_prefix='/auth')
    # app.register_blueprint(owner_bp, url_prefix='/owner')
    # app.register_blueprint(admin_bp, url_prefix='/admin')
    # app.register_blueprint(public_bp)
    # app.register_blueprint(api_bp, url_prefix='/api')

    # --- Serve Uploads ---
    @app.route('/uploads/<path:filename>')
    def serve_uploads(filename):
        return send_from_directory(app.config.get('UPLOAD_FOLDER', 'uploads'), filename)

    # --- Health Check ---
    @app.get("/health")
    def health():
        return {"ok": True}

    return app

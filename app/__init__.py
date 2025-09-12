from flask import Flask
# Blueprints
from .blueprints.public import bp as public_bp
from .blueprints.owner import bp as owner_bp
from .blueprints.admin import bp as admin_bp
from .blueprints.auth import bp as auth_bp
from .blueprints.api import bp as api_bp


# Repositories (SQLAlchemy impl)
from .repositories.sqlalchemy.user_repo_sql import SqlUserRepo
from .repositories.sqlalchemy.property_repo_sql import SqlPropertyRepo
from .repositories.sqlalchemy.approval_repo_sql import SqlApprovalRepo


# Services
from .services.auth_service import AuthService
from .services.property_service import PropertyService
from .services.search_service import SearchService
from .services.approval_service import ApprovalService
from .services.upload_service import UploadService


import os


def register_dependencies(app: Flask) -> None:
"""Simple DI container attached to app.extensions['container']."""
container = {}


# Repos
container['user_repo'] = SqlUserRepo()
container['property_repo'] = SqlPropertyRepo()
container['approval_repo'] = SqlApprovalRepo()


# Services
container['auth_service'] = AuthService(container['user_repo'])
container['property_service'] = PropertyService(container['property_repo'])
container['search_service'] = SearchService(container['property_repo'])
container['approval_service'] = ApprovalService()
container['upload_service'] = UploadService(app.config.get('UPLOAD_FOLDER', 'uploads'))


# expose container
if not hasattr(app, 'extensions'):
app.extensions = {}
app.extensions['container'] = container




def get_service(app: Flask, name: str):
return app.extensions['container'][name]




def create_app() -> Flask:
app = Flask(__name__, instance_relative_config=True)
app.config.from_object(Config)


# Extensions
db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
babel.init_app(app)
limiter.init_app(app)


# DI container
with app.app_context():
register_dependencies(app)


# Blueprints
app.register_blueprint(public_bp)
app.register_blueprint(owner_bp, url_prefix="/owner")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(api_bp, url_prefix="/api")


@app.get("/health")
def health():
return {"ok": True}


return app
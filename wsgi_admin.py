# wsgi_admin.py
from flask import Flask
from core.config import BaseConfig
from admin import admin_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = BaseConfig.ADMIN_SECRET_KEY
    app.register_blueprint(admin_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)

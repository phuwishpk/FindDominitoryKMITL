# wsgi_owner.py
from flask import Flask
from core.config import BaseConfig
from owner import owner_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = BaseConfig.OWNER_SECRET_KEY
    app.register_blueprint(owner_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)

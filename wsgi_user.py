from flask import Flask
from core.config import BaseConfig
from user import user_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = BaseConfig.OWNER_SECRET_KEY
    app.register_blueprint(user_bp)   # <- ต้องมีบรรทัดนี้
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5002)

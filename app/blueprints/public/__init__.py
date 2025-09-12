from flask import Blueprint

bp = Blueprint("public", __name__)

# นำเข้า routes เพื่อให้ Flask รู้จัก endpoint ตอน register blueprint
from . import routes  # noqa: E402,F401

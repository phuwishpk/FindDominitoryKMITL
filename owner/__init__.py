# owner/__init__.py
from flask import Blueprint
import os

owner_bp = Blueprint(
    'owner',
    __name__,
    template_folder=os.path.join('templates'),  # owner/templates
    static_folder=os.path.join('static'),       # owner/static
    static_url_path='/owner/static',            # เรียกด้วย url_for('owner.static', filename='owner.css')
    url_prefix=''                               # route เริ่มต้น (กำหนดใน routes.py)
)

from . import routes  # noqa: E402,F401

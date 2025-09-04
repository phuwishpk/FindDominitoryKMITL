# admin/__init__.py
from flask import Blueprint
import os

# Blueprint ของ Admin แยก template/static ของตัวเอง
admin_bp = Blueprint(
    'admin',
    __name__,
    template_folder=os.path.join('templates'),         # admin/templates
    static_folder=os.path.join('static'),              # admin/static
    static_url_path='/admin/static',                   # เรียกใช้ด้วย url_for('admin.static', filename='admin.css')
    url_prefix=''                                      # route เริ่มต้น (เราจะกำหนดใน routes.py)
)

# นำเข้า routes เพื่อผูกเส้นทางกับ blueprint
from . import routes  # noqa: E402,F401

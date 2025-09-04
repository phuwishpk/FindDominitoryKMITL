# user/__init__.py
from flask import Blueprint
import os

user_bp = Blueprint(
    'user',
    __name__,
    template_folder=os.path.join('templates'),   # user/templates
    static_folder=os.path.join('static'),        # user/static
    static_url_path='/user/static',              # url_for('user.static', filename='user.css')
    url_prefix=''                                # เส้นทางกำหนดใน routes.py
)

from . import routes  # noqa: E402,F401

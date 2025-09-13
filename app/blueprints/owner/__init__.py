from flask import Blueprint
bp = Blueprint("owner", __name__)
from . import routes  # noqa: E402,F401

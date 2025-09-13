from flask import jsonify
from . import bp

@bp.get("/health")
def api_health():
    return jsonify({"api": True, "ok": True})
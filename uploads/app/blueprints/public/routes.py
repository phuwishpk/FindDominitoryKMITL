from flask import render_template, request, current_app
from . import bp

@bp.get("/")
def index():
    svc = current_app.extensions["container"]["search_service"]
    filters = {
        "q": request.args.get("q") or None,
        "min_price": request.args.get("min_price"),
        "max_price": request.args.get("max_price"),
        "room_type": request.args.get("room_type") or None,
        "amenities": request.args.get("amenities") or None,
        "availability": request.args.get("availability") or None,
        "near": request.args.get("near") or None,
        "radius_km": request.args.get("radius_km") or None,
        "sort": request.args.get("sort") or None,
    }
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=12, type=int)
    result = svc.search(filters, page=page, per_page=per_page)
    return render_template("public/index.html", **result)

@bp.get("/property/<int:prop_id>")
def property_detail(prop_id: int):
    repo = current_app.extensions["container"]["property_repo"]
    prop = repo.get(prop_id)
    if not prop:
        return render_template("public/detail.html", prop=None), 404
    return render_template("public/detail.html", prop=prop)

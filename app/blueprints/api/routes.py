from flask import jsonify, request
from . import bp


@bp.get("/properties")
def api_properties():
    filters = request.args.to_dict()
    # TODO: call SearchService.search(filters)
    return jsonify({"items": [], "page": 1, "per_page": 12, "total": 0})
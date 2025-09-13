from flask import render_template
from flask_login import login_required
from . import bp
from app.extensions import admin_required

@bp.get("/")
@login_required
@admin_required
def queue():
    return render_template("admin/queue.html")
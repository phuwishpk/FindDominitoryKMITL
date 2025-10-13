from flask import render_template, request, current_app, redirect, url_for, flash
from flask_login import current_user
from . import bp
# สมมติว่าคุณสร้างไฟล์ review.py ใน app/forms/ แล้ว
from app.forms.review import ReviewForm 

@bp.get("/")
def index():
    svc = current_app.extensions["container"]["search_service"]
    filters = { "q": request.args.get("q") or None }
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=12, type=int)
    result = svc.search(filters, page=page, per_page=per_page)
    return render_template("public/index.html", **result)

@bp.route("/property/<int:prop_id>", methods=["GET", "POST"])
def property_detail(prop_id: int):
    repo = current_app.extensions["container"]["property_repo"]
    review_svc = current_app.extensions["container"]["review_service"]
    prop = repo.get(prop_id)

    if not prop or prop.workflow_status != 'approved':
        return render_template("public/detail.html", prop=None), 404
        
    form = ReviewForm()
    
    if form.validate_on_submit():
        user_id = current_user.ref_id if current_user.is_authenticated else None
        review_svc.add_review(
            property_id=prop.id,
            user_id=user_id,
            comment=form.comment.data,
            rating=int(form.rating.data)
        )
        flash("ขอบคุณสำหรับรีวิวของคุณ")
        return redirect(url_for("public.property_detail", prop_id=prop.id))

    review_data = review_svc.get_reviews_and_average_rating(prop_id)
    
    return render_template("public/detail.html", 
                           prop=prop, 
                           form=form, 
                           reviews=review_data["reviews"], 
                           avg_rating=review_data["average_rating"])    
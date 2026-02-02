from flask import render_template
from flask_login import login_required
from . import operator_bp
from auth.decorators import operator_required
from models import Store

@operator_bp.route("/operator/stores")
@login_required
@operator_required
def store_index():
    stores = Store.query.order_by(Store.created_at.desc()).all()
    return render_template(
        "operator/store_index.html",
        stores=stores
    )

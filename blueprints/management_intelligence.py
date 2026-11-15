"""Read-only Management Intelligence view for an explicitly configured SQLite pilot."""

from pathlib import Path

from flask import Blueprint, abort, current_app, render_template
from flask_login import current_user, login_required

from extensions import db
from mi_v5.vertical_slice import evaluate_case, load_store_period
from utils.permissions import require_capability


management_intelligence_bp = Blueprint("management_intelligence", __name__)


@management_intelligence_bp.get("/management-intelligence")
@login_required
@require_capability("manage.view")
def overview():
    pilot = current_app.config.get("MI_LOCAL_PILOT")
    database = db.engine.url
    if not pilot or database.get_backend_name() != "sqlite" or not database.database:
        abort(404)
    if current_user.is_operator or current_user.store_id != pilot["store_id"]:
        abort(403)

    case = load_store_period(
        Path(database.database),
        legacy_store_id=pilot["store_id"],
        period_start=pilot["period_start"],
        period_end=pilot["period_end"],
    )
    return render_template(
        "local_management_intelligence.html",
        title="Management Intelligence",
        pilot=pilot,
        result=evaluate_case(case).to_dict(),
        schedules_present=bool(case.scheduled_operating_dates),
    )

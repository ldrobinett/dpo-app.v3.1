"""Preview and apply reviewed CDK technician hours."""

import csv
import hashlib
import json
from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from models import ManagedStore, WorkLog
from services.tech_hours_download import compare_tech_hours, comparison_fingerprint, hour_totals, read_tech_hours
from utils.permissions import require_capability


reconciliation_bp = Blueprint("reconciliation", __name__)


def preview_path(identifier):
    return Path(current_app.instance_path) / "tech-hours-previews" / f"{identifier}.json"


@reconciliation_bp.route("/manage/reconcile", methods=["GET", "POST"])
@login_required
@require_capability("worklog.manage")
def reconcile_logs():
    store = db.session.get(ManagedStore, current_user.store_id)
    if store is None:
        abort(403)
    form = FlaskForm()
    if request.method != "POST":
        return download_page(store, form)
    if not form.validate_on_submit():
        flash("Reload the page before submitting the download.", "warning")
        return download_page(store, form)
    if request.form.get("action") == "apply":
        return apply_download(store, form)

    file = request.files.get("dms_file")
    try:
        if not file or not file.filename.lower().endswith(".csv"):
            raise ValueError("Choose a CDK technician hours CSV file.")
        raw = file.stream.read(5_000_001)
        if len(raw) > 5_000_000:
            raise ValueError("Choose a technician hours CSV under 5 MB.")
        detail = read_tech_hours(raw)
        results, missing = compare_tech_hours(store.id, detail)
    except (ValueError, csv.Error) as error:
        flash(str(error), "warning")
        return download_page(store, form)

    identifier = uuid4().hex
    review = dict(id=identifier, store_id=store.id, user_id=current_user.get_id(),
                  name=Path(file.filename.replace(chr(92), "/")).name,
                  sha256=hashlib.sha256(raw).hexdigest(), detail=detail,
                  fingerprint=comparison_fingerprint(results, missing))
    path = preview_path(identifier)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(review), encoding="utf-8")
    prior = session.get("tech_hours_preview")
    session["tech_hours_preview"] = identifier
    if prior:
        preview_path(prior).unlink(missing_ok=True)
    return download_page(store, form, review, results, missing)


def apply_download(store, form):
    identifier = session.get("tech_hours_preview")
    if not identifier or request.form.get("preview_id") != identifier:
        return preview_again("Preview the file before applying hours.")
    path = preview_path(identifier)
    try:
        review = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return preview_again("Preview the file again before applying hours.")
    if review["store_id"] != store.id or review["user_id"] != current_user.get_id():
        abort(403)

    try:
        store.tech_hours_audit_timestamp = datetime.utcnow()
        db.session.flush()
        results, missing = compare_tech_hours(store.id, review["detail"])
        if not missing or comparison_fingerprint(results, missing) != review["fingerprint"]:
            db.session.rollback()
            return preview_again("The Work Log changed since preview. Review the file again before applying hours.")
        db.session.add_all([
            WorkLog(
                team_member_id=row["member_id"], date=date.fromisoformat(row["date"]),
                ro_number=row["ro"], line_item=row["line"],
                actual_time=float(row["actual"]), flat_rate_hours=float(row["sold"]),
                notes=f"CDK RTH {review['sha256'][:16]} · CSV record {row['record']} · Seq {row['sequence'] or '—'}",
            )
            for row in missing
        ])
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("CDK technician hours apply failed")
        return preview_again("No hours were added. Preview the file again and retry.")

    path.unlink(missing_ok=True)
    session.pop("tech_hours_preview", None)
    flash(f"Added {len(missing):,} CDK bookings to Work Log.", "success")
    return download_page(store, form, review, results, missing, applied=True)


def preview_again(message):
    flash(message, "warning")
    return redirect(url_for(".reconcile_logs"))


def download_page(store, form, review=None, results=(), missing=(), applied=False):
    detail = review["detail"] if review else []
    dates = sorted({row["date"] for row in detail})
    return render_template(
        "reconciliation.html", title="Load Tech Hours Download", store=store, form=form, review=review,
        results=results, source_totals=hour_totals(detail), dates=dates, booking_count=len(detail),
        missing_count=len(missing), missing_totals=hour_totals(missing), applied=applied,
    )
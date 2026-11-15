from flask import (
    Blueprint, render_template, url_for,
    flash, redirect, request, jsonify, current_app, session, abort
)
from flask_login import login_required, current_user
from extensions import db
from models import RepairOrder, TeamMember, Team, WorkLog, ASM, ManagedStore
from forms import RouteSheetForm, QuickLogForm
from datetime import date, datetime, timedelta
from utils.permissions import require_capability
import csv
import hashlib
import json
from pathlib import Path
from uuid import uuid4
from flask_wtf import FlaskForm
from sqlalchemy.exc import SQLAlchemyError
from services.route_download import read_download, preview_download, plan_fingerprint
from pytz import timezone

routesheet_bp = Blueprint("routesheet", __name__)


def route_status_color(status):
    key = " ".join((status or "").upper().replace(".", "").replace("-", " ").split())
    if key in {"VEH DISABLED", "VEHICLE DISABLED"} or "HOLD" in key.split():
        return "red"
    if key == "PRE INVOICED":
        return "green"
    if key in {"OPENED", "PREASSIGNED"}:
        return "orange"
    if key in {"READY TO POST", "ALL LAB POSTED", "ALL LABOR POSTED"}:
        return "yellow"
    return "neutral"


def closed_hours_for_pilot(store_id, today):
    pilot = current_app.config.get("MI_LOCAL_PILOT")
    if not pilot or pilot["store_id"] != store_id:
        return None, None
    source = current_app.config.get("ROUTE_CLOSED_HOURS", {})
    totals = source.get(today.isoformat())
    latest = max(source, default=None)
    if not totals:
        return None, latest
    ro_numbers = {ro for ro, _, _ in totals}
    tech_numbers = {tech for _, tech, _ in totals}
    orders = {order.ro_number: order for order in RepairOrder.query.filter(
        RepairOrder.store_id == store_id, RepairOrder.ro_number.in_(ro_numbers),
    )}
    techs = {tech.tech_number: tech for tech in TeamMember.query.join(Team).filter(
        Team.store_id == store_id, TeamMember.tech_number.in_(tech_numbers),
    )}
    rows = []
    for ro, tech_number, hours in totals:
        order = orders.get(ro)
        tech = techs.get(tech_number)
        asm = order.asm if order else None
        team_id = tech.team_id if tech and tech.team_id is not None else (asm.team_id if asm else None)
        rows.append(dict(asm=str(asm.id) if asm else "unassigned",
                         team=str(team_id) if team_id is not None else "unassigned",
                         tech=str(tech.id) if tech else "unassigned", hours=hours))
    return rows, latest

# =====================================================
# MAIN ROUTE SHEET VIEW
# =====================================================
@routesheet_bp.route("/route_sheet", methods=["GET", "POST"])
@login_required
@require_capability("routesheet.view")
def view_sheet():
    store_id = current_user.store_id

    form = RouteSheetForm()
    log_form = QuickLogForm()

    # -----------------------------
    # CREATE NEW REPAIR ORDER
    # -----------------------------
    if form.validate_on_submit() and "submit" in request.form:
        ro = RepairOrder(
            ro_number=form.ro_number.data,
            customer_name=form.customer_name.data,
            vehicle_info=form.vehicle_info.data,
            status=form.status.data,
            team_member_id=form.team_member.data.id if form.team_member.data else None,
            asm_id=form.asm.data.id if form.asm.data else None,
            service_description=form.service_description.data,
            notes=form.notes.data,
            advisor_id=current_user.id,
            store_id=store_id,
        )

        if form.promised_time.data:
            ro.promised_time = form.promised_time.data

        db.session.add(ro)
        db.session.commit()
        flash("Repair Order added to Route Sheet!", "success")
        return redirect(url_for("routesheet.view_sheet"))

    # -----------------------------
    # LOAD DATA
    # -----------------------------
    show_closed = request.args.get("view") == "closed"
    closed_status = db.func.upper(RepairOrder.status) == "CLOSED"
    jobs = (
        RepairOrder.query
        .filter(
            RepairOrder.store_id == store_id,
            closed_status if show_closed else ~closed_status,
        )
        .order_by(RepairOrder.status, RepairOrder.created_at)
        .all()
    )

    all_techs = (
        TeamMember.query
        .join(Team)
        .filter(
            Team.store_id == store_id,
            TeamMember.retired_at.is_(None),
        )
        .order_by(TeamMember.name)
        .all()
    )

    all_asms = (
        ASM.query
        .filter_by(store_id=store_id)
        .order_by(ASM.name)
        .all()
    )
    route_teams = Team.query.filter_by(store_id=store_id).order_by(Team.name).all()

    now = datetime.now(timezone("America/Los_Angeles")).replace(tzinfo=None)
    closed_hours, latest_close_date = closed_hours_for_pilot(store_id, now.date())
    return render_template(
        "route_sheet.html",
        title="Route Sheet",
        form=form,
        log_form=log_form,
        jobs=jobs,
        show_closed=show_closed,
        closed_hours=closed_hours,
        latest_close_date=latest_close_date,
        all_techs=all_techs,
        all_asms=all_asms,
        route_teams=route_teams,
        status_color=route_status_color,
        now=now,
        timedelta=timedelta,
    )

# =====================================================
# EDIT RO DETAILS (MODAL)
# =====================================================
@routesheet_bp.route("/route_sheet/<int:ro_id>/edit_details", methods=["POST"])
@login_required
@require_capability("routesheet.edit")
def edit_ro_details(ro_id):
    ro = RepairOrder.query.get_or_404(ro_id)

    if ro.store_id != current_user.store_id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("routesheet.view_sheet"))

    ro.ro_number = request.form.get("ro_number")
    ro.customer_name = request.form.get("customer_name")
    ro.vehicle_info = request.form.get("vehicle_info")
    ro.service_description = request.form.get("service_description")

    new_notes = request.form.get("notes")
    if new_notes != ro.notes:
        ro.notes = new_notes
        ro.notes_read = False

    tech_id = request.form.get("team_member_id")
    ro.team_member_id = int(tech_id) if tech_id else None

    asm_id = request.form.get("asm_id")
    ro.asm_id = int(asm_id) if asm_id else None

    promised_str = request.form.get("promised_time")
    if promised_str:
        try:
            ro.promised_time = datetime.strptime(promised_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            pass
    else:
        ro.promised_time = None

    db.session.commit()
    flash(f"RO #{ro.ro_number} updated.", "success")
    return redirect(url_for("routesheet.view_sheet"))

# =====================================================
# QUICK LOG WORK FROM ROUTE SHEET
# =====================================================
@routesheet_bp.route("/route_sheet/log_work/<int:ro_id>", methods=["POST"])
@login_required
@require_capability("routesheet.edit")
def log_work_quick(ro_id):
    ro = RepairOrder.query.get_or_404(ro_id)
    form = QuickLogForm()

    if ro.store_id != current_user.store_id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("routesheet.view_sheet"))

    if form.validate_on_submit():
        if not ro.team_member_id:
            flash("No technician assigned.", "danger")
            return redirect(url_for("routesheet.view_sheet"))

        work_log = WorkLog(
            team_member_id=ro.team_member_id,
            date=date.today(),
            ro_number=ro.ro_number,
            flat_rate_hours=form.flat_rate_hours.data,
            actual_time=form.actual_time.data,
            notes=f"From Route Sheet: {form.notes.data}"
            if form.notes.data else "From Route Sheet",
        )

        db.session.add(work_log)
        db.session.commit()
        flash("Work logged successfully.", "success")
    else:
        flash("Error logging work.", "danger")

    return redirect(url_for("routesheet.view_sheet"))

# =====================================================
# UPDATE RO STATUS
# =====================================================
@routesheet_bp.route("/route_sheet/<int:ro_id>/update/<new_status>")
@login_required
@require_capability("routesheet.edit")
def update_status(ro_id, new_status):
    ro = RepairOrder.query.get_or_404(ro_id)

    if ro.store_id != current_user.store_id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("routesheet.view_sheet"))

    ro.status = new_status
    db.session.commit()
    return redirect(url_for("routesheet.view_sheet"))

# =====================================================
# DELETE REPAIR ORDER
# =====================================================
@routesheet_bp.route("/route_sheet/<int:ro_id>/delete", methods=["POST"])
@login_required
@require_capability("routesheet.edit")
def delete_ro(ro_id):
    ro = RepairOrder.query.get_or_404(ro_id)

    if ro.store_id != current_user.store_id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("routesheet.view_sheet"))

    db.session.delete(ro)
    db.session.commit()
    flash("Repair Order removed.", "success")
    return redirect(url_for("routesheet.view_sheet"))

# =====================================================
# CLOSED RO HISTORY
# =====================================================
@routesheet_bp.route("/route_sheet/history")
@login_required
@require_capability("routesheet.view")
def view_history():
    store_id = current_user.store_id

    closed_jobs = (
        RepairOrder.query
        .filter(
            RepairOrder.store_id == store_id,
            RepairOrder.status == "Closed"
        )
        .order_by(RepairOrder.created_at.desc())
        .all()
    )

    return render_template(
        "ro_history.html",
        title="Closed RO History",
        jobs=closed_jobs,
    )

# =====================================================
# MARK NOTES AS READ (AJAX)
# =====================================================
@routesheet_bp.route(
    "/route_sheet/<int:ro_id>/mark_notes_read",
    methods=["POST"]
)
@login_required
@require_capability("routesheet.edit")
def mark_notes_read(ro_id):
    ro = RepairOrder.query.get_or_404(ro_id)

    if ro.store_id != current_user.store_id:
        return jsonify({"success": False}), 403

    ro.notes_read = True
    db.session.commit()
    return jsonify({"success": True})

# =====================================================
# CSV Download of routesheet for audit
# =====================================================

@routesheet_bp.route("/cdk_audit_upload", methods=["GET", "POST"])
@login_required
@require_capability("routesheet.edit")
def cdk_audit_upload():
    store = db.session.get(ManagedStore, current_user.store_id)
    if store is None:
        abort(403)
    form = FlaskForm()
    review = None
    plan = []
    if request.method == "POST":
        if not form.validate_on_submit():
            flash("Reload the page before submitting the download.", "warning")
        elif request.form.get("action") == "apply":
            return apply_route_download(store, form)
        else:
            file = request.files.get("csv_file")
            try:
                if not file or not file.filename.lower().endswith(".csv"):
                    raise ValueError("Choose a CDK Route Sheet CSV file.")
                raw = file.stream.read(5_000_001)
                if len(raw) > 5_000_000:
                    raise ValueError("Choose a Route Sheet CSV under 5 MB.")
                pilot = current_app.config.get("MI_LOCAL_PILOT")
                rows = read_download(raw, hide_customer=bool(
                    current_app.config.get("LOCAL_HIDE_ROUTE_CUSTOMERS") or (pilot and pilot["store_id"] == store.id)
                ))
                plan, _ = preview_download(store.id, rows)
                review = {
                    "id": uuid4().hex, "store_id": store.id, "user_id": current_user.get_id(),
                    "name": Path(file.filename.replace("\\", "/")).name,
                    "sha256": hashlib.sha256(raw).hexdigest(), "rows": rows,
                    "plan": plan_fingerprint(plan),
                }
                folder = Path(current_app.instance_path) / "route-download-previews"
                folder.mkdir(parents=True, exist_ok=True)
                (folder / f"{review['id']}.json").write_text(json.dumps(review), encoding="utf-8")
                prior = session.get("route_download_preview")
                session["route_download_preview"] = review["id"]
                if prior:
                    (folder / f"{prior}.json").unlink(missing_ok=True)
            except (ValueError, csv.Error) as error:
                flash(str(error), "warning")
    return render_template("cdk_upload.html", title="Load Route Sheet Download",
                           form=form, store=store, review=review, plan=plan)


def apply_route_download(store, form):
    identifier = session.get("route_download_preview")
    if not identifier or request.form.get("preview_id") != identifier:
        flash("Preview the file again before applying changes.", "warning")
        return redirect(url_for(".cdk_audit_upload"))
    path = Path(current_app.instance_path) / "route-download-previews" / f"{identifier}.json"
    try:
        review = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        flash("Preview the file again before applying changes.", "warning")
        return redirect(url_for(".cdk_audit_upload"))
    if review["store_id"] != store.id or review["user_id"] != current_user.get_id():
        abort(403)
    plan, existing = preview_download(store.id, review["rows"])
    if plan_fingerprint(plan) != review["plan"]:
        flash("The Route Sheet changed since preview. Review the file again before applying.", "warning")
        return redirect(url_for(".cdk_audit_upload"))
    if not any(row["kind"] in {"New", "Updated", "No change"} for row in plan):
        flash("No CDK rows are ready to apply.", "warning")
        return redirect(url_for(".cdk_audit_upload"))

    timestamp = datetime.utcnow()
    counts = {"New": 0, "Updated": 0}
    for row in plan:
        kind = row["kind"]
        if kind not in counts:
            continue
        if kind == "New":
            order = RepairOrder(store_id=store.id, ro_number=row["ro"], customer_name="Customer omitted")
            db.session.add(order)
        else:
            order = existing[row["ro"]]
        for field, value in row["changes"].items():
            setattr(order, field, datetime.fromisoformat(value) if field == "promised_time" else value)
        order.audited = True
        order.audit_source = "CDK"
        order.audit_timestamp = timestamp
        counts[kind] += 1
    store.routesheet_audit_timestamp = timestamp
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("CDK Route Sheet apply failed")
        flash("Nothing was applied. Preview the file again and retry.", "warning")
        return redirect(url_for(".cdk_audit_upload"))

    path.unlink(missing_ok=True)
    session.pop("route_download_preview", None)
    flash(f"CDK Route Sheet applied. {counts['New']} new, {counts['Updated']} updated.", "success")
    return render_template("cdk_upload.html", title="Load Route Sheet Download",
                           form=form, store=store, review=review, plan=plan, applied=True)

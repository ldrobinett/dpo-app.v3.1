from flask import (
    Blueprint, render_template, url_for,
    flash, redirect, request, jsonify
)
from flask_login import login_required, current_user
from extensions import db
from models import RepairOrder, TeamMember, Team, WorkLog, ASM, ManagedStore
from forms import RouteSheetForm, QuickLogForm
from datetime import date, datetime, timedelta
from utils.permissions import require_capability
from utils.audit import update_audit_timestamp
import csv
import io

CDK_STATUS_MAP = {
    "OPENED": "Dispatch",
    "AUTH. HOLD": "Approval",
    "PREASSIGNED": "Dispatch",
    "VEH. DISABLED": "Parts",
    "WORKING": "Service",
    "READY TO POST": "Warranty",
    "ALL LAB. POSTED": "Ready",
    "PRE-INVOICED": "Ready",
    "CLOSED": "Closed",
}

routesheet_bp = Blueprint("routesheet", __name__)

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
    active_jobs = (
        RepairOrder.query
        .filter(
            RepairOrder.store_id == store_id,
            RepairOrder.status != "Closed"
        )
        .order_by(RepairOrder.status, RepairOrder.created_at)
        .all()
    )

    all_techs = (
        TeamMember.query
        .join(Team)
        .filter(Team.store_id == store_id)
        .order_by(TeamMember.name)
        .all()
    )

    all_asms = (
        ASM.query
        .filter_by(store_id=store_id)
        .order_by(ASM.name)
        .all()
    )

    return render_template(
        "route_sheet.html",
        title="Route Sheet",
        form=form,
        log_form=log_form,
        jobs=active_jobs,
        all_techs=all_techs,
        all_asms=all_asms,
        now=datetime.now(),
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
def cdk_audit_upload():

    if request.method == "POST":

        file = request.files.get("csv_file")

        if not file or file.filename.strip() == "":
            flash("No file selected.", "danger")
            return redirect(request.url)

        stream = io.TextIOWrapper(file.stream, encoding="utf-8", newline=None)
        csv_reader = csv.DictReader(stream)

        updated = 0
        created = 0

        imported_ro_numbers = set()   # ✅ TRACK IMPORTED ROs

        for row in csv_reader:

            ro_number = row.get("RO")
            customer = row.get("Customer")
            model = row.get("Model")
            year = row.get("Year")
            promise = row.get("Promise")
            service = row.get("Service Request")
            cdk_status = row.get("Status Code Desc")

            if not ro_number:
                continue

            imported_ro_numbers.add(ro_number)  # ✅ ADD TO TRACKER

            # ----------------------------------------
            # Convert CDK Status → Internal Status
            # ----------------------------------------
            mapped_status = "Dispatch"

            if cdk_status:
                for status_piece in cdk_status.split(","):
                    status_piece = status_piece.strip()
                    if status_piece in CDK_STATUS_MAP:
                        mapped_status = CDK_STATUS_MAP[status_piece]
                        break

            # ----------------------------------------
            # Convert Promise Time
            # ----------------------------------------
            promised_time = None
            if promise:
                try:
                    promised_time = datetime.strptime(promise, "%m/%d/%Y %H:%M")
                except:
                    pass

            # ----------------------------------------
            # Find Existing RO
            # ----------------------------------------
            ro = RepairOrder.query.filter_by(
                ro_number=ro_number,
                store_id=current_user.store_id
            ).first()

            if ro:
                ro.customer_name = customer
                ro.vehicle_info = f"{year} {model}" if model else ro.vehicle_info
                ro.service_description = service
                ro.promised_time = promised_time
                ro.status = mapped_status

                ro.audited = True
                ro.audit_source = "CDK"
                ro.audit_timestamp = datetime.utcnow()

                updated += 1

            else:
                new_ro = RepairOrder(
                    ro_number=ro_number,
                    customer_name=customer,
                    vehicle_info=f"{year} {model}" if model else "",
                    service_description=service,
                    promised_time=promised_time,
                    status=mapped_status,
                    store_id=current_user.store_id,
                    audited=True,
                    audit_source="CDK",
                    audit_timestamp=datetime.utcnow()
                )

                db.session.add(new_ro)
                created += 1

        # ==================================================
        # CLOSE ROs NOT PRESENT IN THE AUDIT FILE
        # ==================================================
        existing_ros = RepairOrder.query.filter_by(
            store_id=current_user.store_id
        ).all()

        closed_count = 0

        for ro in existing_ros:
            if ro.ro_number not in imported_ro_numbers:
                if ro.status != "Closed":
                    ro.status = "Closed"
                    ro.audit_source = "CDK"
                    ro.audit_timestamp = datetime.utcnow()
                    closed_count += 1

        store = db.session.get(ManagedStore, current_user.store_id)

        if store:
            store.routesheet_audit_timestamp = datetime.utcnow()

        db.session.commit()

        #Update store audit timestamp
        #update_audit_timestamp(current_user.store_id)

        flash(
            f"Audit complete. {updated} updated, {created} created, {closed_count} closed.",
            "success"
        )

        return redirect(url_for("routesheet.view_sheet"))

    return render_template("cdk_upload.html")



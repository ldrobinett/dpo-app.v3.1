from flask import Blueprint, current_app, render_template, url_for, flash, redirect, request
from flask_login import login_required, current_user
from extensions import db
from models import WorkLog, TeamMember, Team
from forms import WorkLogForm
from utils.permissions import require_capability
from datetime import date, timedelta, datetime
from sqlalchemy.orm import joinedload
from pytz import timezone
from .management_intelligence import technician_id_review

worklog_bp = Blueprint("worklog", __name__)

@worklog_bp.route("/work_logs")
@login_required
@require_capability("worklog.manage")
def work_logs():
    page = request.args.get("page", 1, type=int)
    start_date_str = request.args.get("start_date", "").strip()
    end_date_str = request.args.get("end_date", "").strip()
    tech_name = request.args.get("tech_name", "").strip()
    tech_number = request.args.get("tech_number", "").strip()
    ro_number = request.args.get("ro_number", "").strip()
    review = request.args.get("review", "")
    pilot = current_app.config.get("MI_LOCAL_PILOT")
    if pilot and pilot["store_id"] != current_user.store_id:
        pilot = None

    base_query = (
        WorkLog.query
        .options(joinedload(WorkLog.team_member))
        .join(TeamMember)
        .join(Team)
        .filter(Team.store_id == current_user.store_id)
    )

    default_date = datetime.now(timezone("America/Los_Angeles")).date()
    default_start = pilot["period_start"] if pilot else default_date
    default_end = pilot["period_end"] if pilot else default_date
    try:
        start_date = date.fromisoformat(start_date_str) if start_date_str else default_start
        end_date = date.fromisoformat(end_date_str) if end_date_str else (start_date if start_date_str else default_end)
        if end_date < start_date:
            raise ValueError
    except ValueError:
        flash("Enter a valid booking date range. Showing the default dates.", "warning")
        start_date, end_date = default_start, default_end

    base_query = base_query.filter(
        WorkLog.date >= start_date,
        WorkLog.date <= end_date
    )

    if tech_name:
        base_query = base_query.filter(TeamMember.name.ilike(f"%{tech_name}%"))

    if tech_number:
        base_query = base_query.filter(TeamMember.tech_number.ilike(f"%{tech_number}%"))

    if ro_number:
        base_query = base_query.filter(WorkLog.ro_number.ilike(f"%{ro_number}%"))

    checks = {
        "missing-ro": WorkLog.ro_number.is_(None) | (db.func.trim(WorkLog.ro_number) == ""),
        "missing-actual": WorkLog.actual_time.is_(None),
        "negative-sold": WorkLog.flat_rate_hours < 0,
    }
    review_counts = base_query.with_entities(
        *(db.func.count(db.case((check, 1))) for check in checks.values())
    ).one()
    review_counts = dict(zip(checks, review_counts))
    if review in checks:
        base_query = base_query.filter(checks[review])
    else:
        review = ""
    sold_hours, actual_hours = base_query.with_entities(
        db.func.sum(WorkLog.flat_rate_hours), db.func.sum(WorkLog.actual_time),
    ).one()
    pagination = (
        base_query
        .order_by(WorkLog.date.desc(), WorkLog.id.desc())
        .paginate(page=max(1, page), per_page=25, error_out=False)
    )

    return render_template(
        "work_logs.html",
        title="Work Log",
        logs=pagination.items,
        pagination=pagination,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        tech_name=tech_name,
        tech_number=tech_number,
        ro_number=ro_number,
        review=review,
        review_counts=review_counts,
        sold_hours=sold_hours,
        actual_hours=actual_hours,
        pilot=pilot,
        tech_id_review=technician_id_review(pilot),
    )

# =====================================================
# CREATE WORK LOG
# =====================================================

@worklog_bp.route("/work_log/new", methods=["GET", "POST"])
@login_required
@require_capability("worklog.manage")
def new_work_log():
    form = WorkLogForm()

    # Populate technicians for this store only
    form.team_member.query = (
        TeamMember.query
        .join(Team)
        .filter(
            Team.store_id == current_user.store_id,
            TeamMember.retired_at.is_(None),
        )
        .order_by(TeamMember.name)
    )

    if form.validate_on_submit():
        log = WorkLog(
            team_member_id=form.team_member.data.id,
            date=form.date.data,
            ro_number=form.ro_number.data,
            line_item=form.line_item.data,
            flat_rate_hours=form.flat_rate_hours.data,
            actual_time=form.actual_time.data,
            notes=form.notes.data,
        )

        db.session.add(log)
        db.session.commit()
        flash("Work log added successfully!", "success")
        return redirect(url_for("worklog.work_logs"))

    return render_template(
        "create_edit_work_log.html",
        title="New Work Log",
        form=form,
    )

# =====================================================
# EDIT WORK LOG
# =====================================================

@worklog_bp.route("/work_log/<int:log_id>/edit", methods=["GET", "POST"])
@login_required
@require_capability("worklog.manage")
def edit_work_log(log_id):
    log = WorkLog.query.get_or_404(log_id)

    # Store safety check
    if log.team_member.team.store_id != current_user.store_id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("worklog.work_logs"))

    form = WorkLogForm(obj=log)
    form.team_member.query = (
        TeamMember.query
        .join(Team)
        .filter(
            Team.store_id == current_user.store_id,
            TeamMember.retired_at.is_(None),
        )
        .order_by(TeamMember.name)
    )

    if form.validate_on_submit():
        form.populate_obj(log)
        log.team_member_id = form.team_member.data.id
        db.session.commit()
        flash("Work log updated successfully!", "success")
        return redirect(url_for("worklog.work_logs"))

    return render_template(
        "create_edit_work_log.html",
        title="Edit Work Log",
        form=form,
    )

# =====================================================
# DELETE WORK LOG
# =====================================================

@worklog_bp.route("/work_log/<int:log_id>/delete", methods=["POST"])
@login_required
@require_capability("worklog.manage")
def delete_work_log(log_id):
    log = WorkLog.query.get_or_404(log_id)

    # Store safety check
    if log.team_member.team.store_id != current_user.store_id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("worklog.work_logs"))

    db.session.delete(log)
    db.session.commit()
    flash("Work log deleted.", "success")
    return redirect(url_for("worklog.work_logs"))

from flask import Blueprint, render_template, url_for, flash, redirect
from flask_login import login_required, current_user
from extensions import db
from models import WorkLog, TeamMember, Team
from forms import WorkLogForm
from utils.permissions import require_capability

worklog_bp = Blueprint("worklog", __name__)

# =====================================================
# WORK LOG LIST
# =====================================================

@worklog_bp.route("/work_logs")
@login_required
@require_capability("worklog.manage")
def work_logs():
    logs = (
        WorkLog.query
        .join(TeamMember)
        .join(Team)
        .filter(Team.store_id == current_user.store_id)
        .order_by(WorkLog.date.desc(), WorkLog.id.desc())
        .all()
    )

    return render_template(
        "work_logs.html",
        title="Work Logs",
        logs=logs,
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
        .filter(Team.store_id == current_user.store_id)
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
        .filter(Team.store_id == current_user.store_id)
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

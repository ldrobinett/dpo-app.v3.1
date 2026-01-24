from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_required, current_user, AnonymousUserMixin
from extensions import db
from models import WorkLog, TeamMember, Team
from forms import WorkLogForm
from datetime import date

worklog_bp = Blueprint('worklog', __name__)

@worklog_bp.route("/work_logs")
@login_required
def work_logs():
    if not current_user.is_authenticated or isinstance(current_user._get_current_object(), AnonymousUserMixin):
        return redirect(url_for('auth.login'))
        
    # Show logs for the current user's store
    store_id = current_user.store_id
    logs = WorkLog.query.join(TeamMember).join(Team).filter(
        Team.store_id == store_id
    ).order_by(WorkLog.date.desc(), WorkLog.created_at.desc() if hasattr(WorkLog, 'created_at') else WorkLog.date.desc()).all()
    
    return render_template('work_logs.html', title='Work Logs', logs=logs)

@worklog_bp.route("/work_log/new", methods=['GET', 'POST'])
@login_required
def new_work_log():
    form = WorkLogForm()
    # Populate QuerySelectField with current store's techs
    form.team_member.query = TeamMember.query.join(Team).filter(Team.store_id == current_user.store_id).order_by(TeamMember.name)

    if form.validate_on_submit():
        log = WorkLog(
            team_member_id=form.team_member.data.id,
            date=form.date.data,
            ro_number=form.ro_number.data,
            line_item=form.line_item.data,
            flat_rate_hours=form.flat_rate_hours.data,
            actual_time=form.actual_time.data, # <--- UPDATED FIELD
            notes=form.notes.data
        )
        db.session.add(log)
        db.session.commit()
        flash('Work log added successfully!', 'success')
        return redirect(url_for('worklog.work_logs'))
        
    return render_template('create_edit_work_log.html', title='New Work Log', form=form)

@worklog_bp.route("/work_log/<int:log_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_work_log(log_id):
    log = WorkLog.query.get_or_404(log_id)
    # Check ownership logic here if needed (via team_member -> team -> store_id)
    
    form = WorkLogForm(obj=log)
    form.team_member.query = TeamMember.query.join(Team).filter(Team.store_id == current_user.store_id).order_by(TeamMember.name)

    if form.validate_on_submit():
        form.populate_obj(log)
        # Ensure relations are set if populate_obj doesn't handle the object relation directly
        log.team_member_id = form.team_member.data.id
        db.session.commit()
        flash('Work log updated!', 'success')
        return redirect(url_for('worklog.work_logs'))
        
    return render_template('create_edit_work_log.html', title='Edit Work Log', form=form)

@worklog_bp.route("/work_log/<int:log_id>/delete", methods=['POST'])
@login_required
def delete_work_log(log_id):
    log = WorkLog.query.get_or_404(log_id)
    db.session.delete(log)
    db.session.commit()
    flash('Work log deleted.', 'success')
    return redirect(url_for('worklog.work_logs'))

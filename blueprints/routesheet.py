from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_required, current_user, AnonymousUserMixin
from extensions import db
from models import RepairOrder, TeamMember, Team, WorkLog, ASM
from forms import RouteSheetForm, QuickLogForm
from datetime import date, datetime, timedelta

routesheet_bp = Blueprint('routesheet', __name__)

@routesheet_bp.route("/route_sheet", methods=['GET', 'POST'])
@login_required
def view_sheet():
    if not current_user.is_authenticated or isinstance(current_user._get_current_object(), AnonymousUserMixin):
        return redirect(url_for('auth.login'))

    store_id = current_user.store_id
    
    form = RouteSheetForm() 
    log_form = QuickLogForm()
    
    # --- HANDLE NEW RO CREATION ---
    if form.validate_on_submit() and 'submit' in request.form:
        ro = RepairOrder(
            ro_number=form.ro_number.data,
            customer_name=form.customer_name.data,
            vehicle_info=form.vehicle_info.data,
            status=form.status.data,
            
            # Relationships
            team_member_id=form.team_member.data.id if form.team_member.data else None,
            asm_id=form.asm.data.id if form.asm.data else None,
            
            # Details
            service_description=form.service_description.data,
            notes=form.notes.data,
            
            # Metadata
            advisor_id=current_user.id,
            store_id=store_id
        )
        
        # Handle Promised Time
        if form.promised_time.data:
            ro.promised_time = form.promised_time.data
            
        db.session.add(ro)
        db.session.commit()
        flash('Repair Order added to Route Sheet!', 'success')
        return redirect(url_for('routesheet.view_sheet'))

    # --- RETRIEVE DATA ---
    
    # 1. Active Jobs (Excluding Closed)
    active_jobs = RepairOrder.query.filter(
        RepairOrder.store_id == store_id,
        RepairOrder.status != 'Closed'
    ).order_by(RepairOrder.status, RepairOrder.created_at).all()

    # 2. Lists for Edit Modal Dropdowns
    all_techs = TeamMember.query.join(Team).filter(Team.store_id == store_id).order_by(TeamMember.name).all()
    all_asms = ASM.query.filter_by(store_id=store_id).order_by(ASM.name).all()

    return render_template('route_sheet.html', 
                           title='Route Sheet', 
                           form=form, 
                           log_form=log_form,
                           jobs=active_jobs,
                           all_techs=all_techs,
                           all_asms=all_asms,
                           now=datetime.now(),
                           timedelta=timedelta)

@routesheet_bp.route("/route_sheet/<int:ro_id>/edit_details", methods=['POST'])
@login_required
def edit_ro_details(ro_id):
    """
    Handles edits from the modal on the Route Sheet.
    """
    ro = RepairOrder.query.get_or_404(ro_id)
    if ro.store_id != current_user.store_id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('routesheet.view_sheet'))
    
    # Update standard text fields
    ro.ro_number = request.form.get('ro_number')
    ro.customer_name = request.form.get('customer_name')
    ro.vehicle_info = request.form.get('vehicle_info')
    ro.service_description = request.form.get('service_description')
    
    # Update Notes (Reset read status if changed)
    new_notes = request.form.get('notes')
    if new_notes != ro.notes:
        ro.notes = new_notes
        ro.notes_read = False
    
    # Update Relationships
    tech_id = request.form.get('team_member_id')
    ro.team_member_id = int(tech_id) if tech_id else None
    
    asm_id = request.form.get('asm_id')
    ro.asm_id = int(asm_id) if asm_id else None
    
    # Update Promised Time
    promised_str = request.form.get('promised_time')
    if promised_str:
        try:
            ro.promised_time = datetime.strptime(promised_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            pass 
    else:
        ro.promised_time = None
            
    db.session.commit()
    flash(f'RO #{ro.ro_number} updated successfully.', 'success')
    return redirect(url_for('routesheet.view_sheet'))

@routesheet_bp.route("/route_sheet/log_work/<int:ro_id>", methods=['POST'])
@login_required
def log_work_quick(ro_id):
    """Creates a WorkLog entry directly from the Route Sheet."""
    ro = RepairOrder.query.get_or_404(ro_id)
    form = QuickLogForm()
    
    if form.validate_on_submit():
        if not ro.team_member_id:
            flash('Cannot log work: No Technician assigned to this RO.', 'danger')
            return redirect(url_for('routesheet.view_sheet'))

        # Create the Work Log
        work_log = WorkLog(
            team_member_id=ro.team_member_id,
            date=date.today(),
            ro_number=ro.ro_number,
            flat_rate_hours=form.flat_rate_hours.data,
            actual_time=form.actual_time.data,
            notes=f"From Route Sheet: {form.notes.data}" if form.notes.data else "From Route Sheet"
        )
        
        db.session.add(work_log)
        db.session.commit()
        flash(f'Logged {form.flat_rate_hours.data} hours for {ro.ro_number}', 'success')
    else:
        flash('Error logging work. Please check inputs.', 'danger')
        
    return redirect(url_for('routesheet.view_sheet'))

@routesheet_bp.route("/route_sheet/<int:ro_id>/update/<new_status>")
@login_required
def update_status(ro_id, new_status):
    ro = RepairOrder.query.get_or_404(ro_id)
    if ro.store_id != current_user.store_id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('routesheet.view_sheet'))
        
    ro.status = new_status
    db.session.commit()
    return redirect(url_for('routesheet.view_sheet'))

@routesheet_bp.route("/route_sheet/<int:ro_id>/delete", methods=['POST'])
@login_required
def delete_ro(ro_id):
    ro = RepairOrder.query.get_or_404(ro_id)
    db.session.delete(ro)
    db.session.commit()
    flash('RO Removed.', 'success')
    return redirect(url_for('routesheet.view_sheet'))

@routesheet_bp.route("/route_sheet/history")
@login_required
def view_history():
    if not current_user.is_authenticated or isinstance(current_user._get_current_object(), AnonymousUserMixin):
        return redirect(url_for('auth.login'))

    store_id = current_user.store_id
    
    closed_jobs = RepairOrder.query.filter(
        RepairOrder.store_id == store_id,
        RepairOrder.status == 'Closed'
    ).order_by(RepairOrder.created_at.desc()).all()

    return render_template('ro_history.html', title='Closed RO History', jobs=closed_jobs)

@routesheet_bp.route("/route_sheet/<int:ro_id>/mark_notes_read", methods=['POST'])
@login_required
def mark_notes_read(ro_id):
    """AJAX endpoint to mark notes as read without reloading page"""
    ro = RepairOrder.query.get_or_404(ro_id)
    if ro.store_id == current_user.store_id:
        ro.notes_read = True
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 403
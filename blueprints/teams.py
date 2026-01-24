from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_required, current_user, AnonymousUserMixin
from extensions import db
from models import Team, TeamMember, ASM
from forms import TeamForm, TeamMemberForm, ASMForm

teams_bp = Blueprint('teams', __name__)

# ==========================================
# TEAM MANAGEMENT ROUTES
# ==========================================

@teams_bp.route("/teams")
@login_required
def teams():
    if not current_user.is_authenticated or isinstance(current_user._get_current_object(), AnonymousUserMixin):
        return redirect(url_for('auth.login'))
    
    form = TeamForm()
    all_teams = Team.query.filter_by(store_id=current_user.store_id).order_by(Team.name).all()
    return render_template('teams.html', title='Manage Teams', teams=all_teams, form=form)

@teams_bp.route("/team/new", methods=['GET', 'POST'])
@login_required
def new_team():
    form = TeamForm()
    if form.validate_on_submit():
        team = Team(name=form.name.data, store_id=current_user.store_id)
        db.session.add(team)
        db.session.commit()
        flash('Team created successfully!', 'success')
        return redirect(url_for('teams.teams'))
    return render_template('create_edit_team.html', title='New Team', form=form)

@teams_bp.route("/team/<int:team_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_team(team_id):
    team = Team.query.get_or_404(team_id)
    if team.store_id != current_user.store_id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('teams.teams'))
        
    form = TeamForm(obj=team)
    if form.validate_on_submit():
        team.name = form.name.data
        db.session.commit()
        flash('Team updated successfully!', 'success')
        return redirect(url_for('teams.teams'))
    return render_template('create_edit_team.html', title='Edit Team', form=form)

@teams_bp.route("/team/<int:team_id>/delete", methods=['POST'])
@login_required
def delete_team(team_id):
    team = Team.query.get_or_404(team_id)
    if team.store_id != current_user.store_id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('teams.teams'))
        
    db.session.delete(team)
    db.session.commit()
    flash('Team deleted successfully!', 'success')
    return redirect(url_for('teams.teams'))

# ==========================================
# TEAM MEMBER ROUTES
# ==========================================

@teams_bp.route("/team_members")
@login_required
def team_members():
    if not current_user.is_authenticated or isinstance(current_user._get_current_object(), AnonymousUserMixin):
        return redirect(url_for('auth.login'))
        
    form = TeamMemberForm()
    all_members = TeamMember.query.join(Team).filter(Team.store_id == current_user.store_id).order_by(Team.name, TeamMember.name).all()
    return render_template('team_members.html', title='Manage Team Members', members=all_members, form=form)

@teams_bp.route("/team_member/new", methods=['GET', 'POST'])
@login_required
def new_team_member():
    form = TeamMemberForm()
    form.team.query = Team.query.filter_by(store_id=current_user.store_id).order_by(Team.name)
    
    if form.validate_on_submit():
        member = TeamMember(
            name=form.name.data,
            tech_number=form.tech_number.data,
            team=form.team.data,
            tech_level=form.tech_level.data,
            dpo_calculation_mode=form.dpo_calculation_mode.data,
            daily_production_objective=form.daily_production_objective.data,
            hist_frh_total=form.hist_frh_total.data,
            hist_days_in_period=form.hist_days_in_period.data,
            hist_training_days=form.hist_training_days.data,
            hist_vacation_days=form.hist_vacation_days.data,
            expected_lift_percent=form.expected_lift_percent.data
        )
        db.session.add(member)
        db.session.commit()
        flash('Team member created successfully!', 'success')
        return redirect(url_for('teams.team_members'))
    
    # FIX: Pass calculated_dpo=0.0 for new members (since they don't exist yet)
    return render_template('create_edit_team_member.html', 
                           title='New Team Member', 
                           form=form, 
                           previous_dpo=0.0, 
                           calculated_dpo=0.0, # <--- ADDED THIS
                           member=None)

@teams_bp.route("/team_member/<int:member_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_team_member(member_id):
    member = TeamMember.query.get_or_404(member_id)
    if member.team and member.team.store_id != current_user.store_id:
         flash('Unauthorized access', 'danger')
         return redirect(url_for('teams.team_members'))

    form = TeamMemberForm(obj=member)
    form.team.query = Team.query.filter_by(store_id=current_user.store_id).order_by(Team.name)
    
    if form.validate_on_submit():
        form.populate_obj(member)
        db.session.commit()
        flash('Team member updated successfully!', 'success')
        return redirect(url_for('teams.team_members'))
    
    # FIX: Calculate previous_dpo and calculated_dpo from the existing member object
    previous_dpo = member.daily_production_objective or 0.0
    calculated_dpo_val = member.calculated_dpo # Uses the property from models.py
    
    # FIX: Pass 'calculated_dpo' to the template
    return render_template('create_edit_team_member.html', 
                           title='Edit Team Member', 
                           form=form, 
                           previous_dpo=previous_dpo, 
                           calculated_dpo=calculated_dpo_val, # <--- ADDED THIS
                           member=member)

@teams_bp.route("/team_member/<int:member_id>/delete", methods=['POST'])
@login_required
def delete_team_member(member_id):
    member = TeamMember.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    flash('Team member deleted successfully!', 'success')
    return redirect(url_for('teams.team_members'))

# ==========================================
# ASM (SERVICE ADVISOR) MANAGEMENT ROUTES
# ==========================================

@teams_bp.route("/asms")
@login_required
def view_asms():
    if not current_user.is_authenticated or isinstance(current_user._get_current_object(), AnonymousUserMixin):
        return redirect(url_for('auth.login'))
    
    form = ASMForm()
    asms = ASM.query.filter_by(store_id=current_user.store_id)\
        .join(Team).order_by(Team.name, ASM.name).all()
        
    return render_template('asms.html', title='Service Advisors', asms=asms, form=form)

@teams_bp.route("/asm/new", methods=['GET', 'POST'])
@login_required
def create_asm():
    form = ASMForm()
    form.team.query = Team.query.filter_by(store_id=current_user.store_id).order_by(Team.name)
    
    if form.validate_on_submit():
        asm = ASM(
            name=form.name.data,
            asm_number=form.asm_number.data,
            team_id=form.team.data.id,
            store_id=current_user.store_id
        )
        db.session.add(asm)
        db.session.commit()
        flash(f'Service Advisor {asm.name} added!', 'success')
        return redirect(url_for('teams.view_asms'))
        
    return render_template('create_edit_asm.html', title='Add Service Advisor', form=form)

@teams_bp.route("/asm/<int:asm_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_asm(asm_id):
    asm = ASM.query.get_or_404(asm_id)
    if asm.store_id != current_user.store_id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('teams.view_asms'))
        
    form = ASMForm(obj=asm)
    form.team.query = Team.query.filter_by(store_id=current_user.store_id).order_by(Team.name)
    
    if form.validate_on_submit():
        asm.name = form.name.data
        asm.asm_number = form.asm_number.data
        asm.team_id = form.team.data.id
        
        db.session.commit()
        flash('Service Advisor updated!', 'success')
        return redirect(url_for('teams.view_asms'))
        
    return render_template('create_edit_asm.html', title='Edit Service Advisor', form=form)

@teams_bp.route("/asm/<int:asm_id>/delete", methods=['POST'])
@login_required
def delete_asm(asm_id):
    asm = ASM.query.get_or_404(asm_id)
    if asm.store_id != current_user.store_id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('teams.view_asms'))
        
    db.session.delete(asm)
    db.session.commit()
    flash('Service Advisor deleted.', 'success')
    return redirect(url_for('teams.view_asms'))

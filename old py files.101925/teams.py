from flask import Blueprint, render_template, url_for, flash, redirect
from flask_login import login_required
from extensions import db
from models import Team, TeamMember, ProductionObjectiveMemo
from forms import TeamForm, TeamMemberForm

# Create the Blueprint
teams_bp = Blueprint('teams', __name__)

@teams_bp.route("/teams", methods=['GET', 'POST'])
@login_required
def teams():
    form = TeamForm()
    
    if form.validate_on_submit():
        team = Team(name=form.name.data)
        db.session.add(team)
        db.session.commit()
        flash('Team created successfully!', 'success')
        return redirect(url_for('teams.teams')) # Use 'teams.teams'

    all_teams = Team.query.all()
    
    return render_template('teams.html', title='Teams', form=form, all_teams=all_teams)

@teams_bp.route("/team/new", methods=['GET', 'POST'])
@login_required
def new_team():
    form = TeamForm()
    if form.validate_on_submit():
        team = Team(name=form.name.data)
        db.session.add(team)
        db.session.commit()
        flash('Team created successfully!', 'success')
        return redirect(url_for('teams.teams')) # Redirect to teams overview
    return render_template('create_edit_team.html', title='New Team', form=form)

@teams_bp.route("/team/<int:team_id>/add_member", methods=['GET', 'POST'])
@login_required
def add_member_to_team(team_id):
    team = Team.query.get_or_404(team_id)
    form = TeamMemberForm()
    # Pre-select the team in the form
    form.team.data = team

    if form.validate_on_submit():
        new_member = TeamMember(
            name=form.name.data,
            team_id=team.id,
            tech_level=form.tech_level.data,
            daily_production_objective=form.daily_production_objective.data
        )
        db.session.add(new_member)
        db.session.commit()
        flash(f'Team member {new_member.name} added to {team.name} successfully!', 'success')
        return redirect(url_for('teams.teams'))

    return render_template('add_member_to_team.html', title=f'Add Member to {team.name}', form=form, team=team)

@teams_bp.route("/team/<int:team_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_team(team_id):
    team = Team.query.get_or_404(team_id)
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
    db.session.delete(team)
    db.session.commit()
    flash('Team deleted successfully!', 'success')
    return redirect(url_for('teams.teams'))

@teams_bp.route("/team_members", methods=['GET', 'POST'])
@login_required
def team_members():
    form = TeamMemberForm()
    
    if form.validate_on_submit():
        selected_team = form.team.data
        
        new_member = TeamMember(
            name=form.name.data,
            team_id=selected_team.id if selected_team else None,
            tech_level=form.tech_level.data,
            daily_production_objective=form.daily_production_objective.data
        )
        db.session.add(new_member)
        db.session.commit()
        flash('Team member added successfully!', 'success')
        return redirect(url_for('teams.team_members')) # Use 'teams.team_members'
    
    all_members = TeamMember.query.all()
    
    return render_template('team_members.html', form=form, team_members=all_members)

@teams_bp.route("/team_member/<int:member_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_team_member(member_id):
    member = TeamMember.query.get_or_404(member_id)
    form = TeamMemberForm(obj=member)
    
    if form.validate_on_submit():
        # Check if objective has changed to create a memo
        if form.daily_production_objective.data != member.daily_production_objective:
            memo = ProductionObjectiveMemo(
                team_member_id=member.id,
                previous_objective=member.daily_production_objective
            )
            db.session.add(memo)

        member.name = form.name.data
        member.team = form.team.data
        member.tech_level = form.tech_level.data
        member.daily_production_objective = form.daily_production_objective.data
        
        db.session.commit()
        flash('Team Member updated successfully!', 'success')
        return redirect(url_for('teams.team_members'))
        
    return render_template('create_edit_team_member.html', title='Edit Team Member', form=form)

@teams_bp.route("/team_member/<int:member_id>/delete", methods=['POST'])
@login_required
def delete_team_member(member_id):
    member = TeamMember.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    flash('Team Member deleted successfully!', 'success')
    return redirect(url_for('teams.team_members')) # Redirect to team members overview

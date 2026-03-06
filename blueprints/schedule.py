from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_required, current_user
from extensions import db
from models import ScheduleEntry, Team, TeamMember, TeamSchedule, Holiday
from forms import (
    ScheduleEntryForm, TeamScheduleForm, RecurringScheduleForm,
    ScheduleEntryFilterForm
)
from datetime import date, time, timedelta, datetime
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from sqlalchemy.orm import joinedload
import calendar # Needed for dynamic calendar logic

# Create the Blueprint
schedule_bp = Blueprint('schedule', __name__)

# --- HOLIDAY HELPER FUNCTIONS ---

def get_holiday_dates(year, start_month, end_month):
    """
    Retrieves and calculates all fixed and dynamic holiday dates within a year/month range.
    """
    holiday_dates = set()

    # Static Holidays
    static_holidays = {
        (1, 1): "New Years Day",
        (7, 4): "Fourth of July",
        (12, 25): "Christmas"
    }

    # Iterate through all months in the required range
    for month in range(start_month, end_month + 1):

        # 1. Static Holidays
        static_day_tuple = (month, 1) # Simplified check for 1st of month (New Years)
        if static_day_tuple in static_holidays and month == 1:
            try:
                holiday_dates.add(date(year, month, 1))
            except ValueError:
                pass

        static_day_tuple = (month, 4) # Simplified check for 4th of month (July 4th)
        if static_day_tuple in static_holidays and month == 7:
            try:
                holiday_dates.add(date(year, month, 4))
            except ValueError:
                pass

        static_day_tuple = (month, 25) # Simplified check for 25th of month (Christmas)
        if static_day_tuple in static_holidays and month == 12:
            try:
                holiday_dates.add(date(year, month, 25))
            except ValueError:
                pass


        # 2. Thanksgiving (Fourth Thursday of November)
        if month == 11:
            # We are looking for the 4th Thursday. Thursday is calendar.THURSDAY (3)
            c = calendar.Calendar(calendar.MONDAY) # Start week on Monday (0)

            # Use the CORRECT method: monthdayscalendar()
            occurrence_count = 0

            for week in c.monthdayscalendar(year, 11): # <-- FIX: Changed to monthdayscalendar()
                # The index for Thursday is 3 (Mon=0, Tue=1, Wed=2, Thu=3)
                day_of_week_index = 3
                day = week[day_of_week_index]

                # If day is > 0, it's a date in November
                if day > 0:
                    occurrence_count += 1
                    if occurrence_count == 4:
                        holiday_dates.add(date(year, 11, day))
                        break

    return holiday_dates


def get_team_member_choices(store_id):
    """Helper to fetch member objects for QuerySelectField choices."""
    return TeamMember.query.join(Team).filter(Team.store_id == store_id).order_by(TeamMember.name).all()

# --- ROUTES ---

@schedule_bp.route("/schedules", methods=['GET'])
@login_required
def schedules():
    filter_form = ScheduleEntryFilterForm(request.args)

    today = date.today()
    target_year = today.year
    target_month = today.month

    if filter_form.month_filter.data:
        try:
            year_str, month_str = filter_form.month_filter.data.split('-')
            target_year = int(year_str)
            target_month = int(month_str)
        except ValueError:
            pass

    filter_form.month_filter.data = f"{target_year:04d}-{target_month:02d}"

    start_date = date(target_year, target_month, 1)
    end_date = start_date + relativedelta(months=1) - timedelta(days=1)

    query = ScheduleEntry.query.options(
        joinedload(ScheduleEntry.team_member).joinedload(TeamMember.team)
    )

    query = query.filter(
        ScheduleEntry.date >= start_date,
        ScheduleEntry.date <= end_date
    )

    if filter_form.team.data and filter_form.team.data.id:
        team_id_to_filter = filter_form.team.data.id
        query = query.join(TeamMember).filter(TeamMember.team_id == team_id_to_filter)

    if filter_form.team_member.data and filter_form.team_member.data.id:
        member_id = filter_form.team_member.data.id
        query = query.filter(ScheduleEntry.team_member_id == member_id)

    all_entries = query.join(TeamMember).join(Team).order_by(
        Team.name,
        ScheduleEntry.date,
        TeamMember.name
    ).all()

    team_schedule = defaultdict(lambda: defaultdict(list))

    for entry in all_entries:
        if entry.team_member and entry.team_member.team:
            team_name = entry.team_member.team.name
            date_str = entry.date.strftime('%Y-%m-%d')
            team_schedule[team_name][date_str].append(entry)

    return render_template('schedules.html',
                             title=f'Team Schedules for {start_date.strftime("%B %Y")}',
                             team_schedule=team_schedule,
                             filter_form=filter_form)

@schedule_bp.route("/schedule_calendar")
@login_required
def schedule_calendar():
    selected_team_id = request.args.get('team_id', default=None, type=int)

    all_teams = Team.query.order_by(Team.name).all()
    team_name_map = {team.id: team.name for team in all_teams}

    query = ScheduleEntry.query.options(
        joinedload(ScheduleEntry.team_member).joinedload(TeamMember.team)
    )

    all_schedules = query.order_by(ScheduleEntry.date, ScheduleEntry.start_time).all()

    events = []

    def format_time(dt):
        if not dt: return ""
        hour = dt.strftime('%I').lstrip('0')
        ampm = dt.strftime('%p')[0].lower()
        return f"{hour}{ampm}"

    if selected_team_id:
        # FILTERED VIEW
        for schedule in all_schedules:
            if schedule.team_member and schedule.team_member.team_id == selected_team_id:
                # Determine styling based on schedule_type
                if schedule.schedule_type == 'PTO':
                    event_class = 'bg-info'
                    title_suffix = " (PTO)"
                elif schedule.schedule_type == 'TRAINING':
                    event_class = 'bg-warning'
                    title_suffix = " (Training)"
                elif schedule.schedule_type == 'HOLIDAY':
                    event_class = 'bg-danger'
                    title_suffix = " (Holiday)"
                else:
                    event_class = ''
                    title_suffix = ""

                start_datetime = datetime.combine(schedule.date, schedule.start_time) if schedule.start_time else datetime.combine(schedule.date, time(8, 0))
                end_datetime = datetime.combine(schedule.date, schedule.end_time) if schedule.end_time else start_datetime + timedelta(hours=1)
                start_str = format_time(start_datetime)
                end_str = format_time(end_datetime)

                title = f"{schedule.team_member.name} ({start_str} - {end_str}){title_suffix}"

                events.append({
                    'title': title,
                    'start': start_datetime.isoformat(),
                    'end': end_datetime.isoformat(),
                    'notes': schedule.notes,
                    'className': event_class
                })
    else:
        # DEFAULT VIEW (Grouped by Team)
        grouped_schedules = defaultdict(lambda: defaultdict(list))
        for s in all_schedules:
            if s.team_member and s.team_member.team_id:
                grouped_schedules[s.date][s.team_member.team_id].append(s)

        for date_val, teams_on_date in grouped_schedules.items():
            for team_id, schedules_for_team in teams_on_date.items():
                if not schedules_for_team: continue
                earliest_start = min(s.start_time for s in schedules_for_team if s.start_time) if any(s.start_time for s in schedules_for_team) else time(8, 0)
                latest_end = max(s.end_time for s in schedules_for_team if s.end_time) if any(s.end_time for s in schedules_for_team) else time(17, 0)
                start_datetime = datetime.combine(date_val, earliest_start)
                end_datetime = datetime.combine(date_val, latest_end)
                team_name = team_name_map.get(team_id, "Unknown Team")
                title_suffix = f" ({schedules_for_team[0].schedule_type})" if schedules_for_team[0].schedule_type != 'WORK' else "" # Indicate Non-Work Day
                start_str = format_time(start_datetime)
                end_str = format_time(end_datetime)
                title = f"{team_name} ({start_str} - {end_str}){title_suffix}"
                events.append({
                    'title': title,
                    'start': start_datetime.isoformat(),
                    'end': end_datetime.isoformat(),
                })

    return render_template('schedule_calendar.html',
                             title='Schedule Calendar',
                             events=events,
                             all_teams=all_teams,
                             selected_team_id=selected_team_id)

# NOTE: The combined route logic is not being used in your current setup, but good practice is to define it.
@schedule_bp.route("/schedule/entry/new_combined", methods=['GET', 'POST'], defaults={'entry_id': None})
@schedule_bp.route("/schedule/entry/edit_combined/<int:entry_id>", methods=['GET', 'POST'])
@login_required
def create_edit_schedule_entry_combined(entry_id):
    store_id = current_user.store_id

    if entry_id:
        entry = ScheduleEntry.query.get_or_404(entry_id)
        form = ScheduleEntryForm(obj=entry)
        form.date.data = entry.date
    else:
        entry = ScheduleEntry()
        form = ScheduleEntryForm()

    # Populate choices for QuerySelectField
    form.team_member.choices = get_team_member_choices(store_id)

    if form.validate_on_submit():
        # QuerySelectField returns the model object, so we access its id
        entry.team_member_id = form.team_member.data.id if form.team_member.data else None
        entry.date = form.date.data
        entry.start_time = form.start_time.data
        entry.end_time = form.end_time.data
        entry.lunch_start = form.lunch_start.data
        entry.lunch_end = form.lunch_end.data
        entry.notes = form.notes.data

        # --- NEW LOGIC: Save the Schedule Type ---
        entry.schedule_type = form.schedule_type.data
        # ----------------------------------------

        db.session.add(entry)
        db.session.commit()
        flash('Schedule entry saved successfully.', 'success')
        return redirect(url_for('schedule.schedule_calendar'))

    return render_template('create_edit_schedule_entry.html', form=form, title='Schedule Entry', is_edit=entry_id is not None)


@schedule_bp.route("/schedule/new", methods=['GET', 'POST'])
@login_required
def new_schedule_entry():
    store_id = current_user.store_id
    form = ScheduleEntryForm()
    # Populate choices for QuerySelectField manually
    form.team_member.choices = get_team_member_choices(store_id)

    if form.validate_on_submit():
        entry = ScheduleEntry()
        # QuerySelectField returns model object, manually set ID
        entry.team_member_id = form.team_member.data.id if form.team_member.data else None

        # Populate matching fields
        entry.date = form.date.data
        entry.start_time = form.start_time.data
        entry.end_time = form.end_time.data
        entry.lunch_start = form.lunch_start.data
        entry.lunch_end = form.lunch_end.data
        entry.notes = form.notes.data

        # --- NEW LOGIC: Save the Schedule Type ---
        entry.schedule_type = form.schedule_type.data
        # ----------------------------------------

        db.session.add(entry)
        db.session.commit()
        flash('Schedule entry created successfully!', 'success')
        return redirect(url_for('schedule.schedules'))

    return render_template('create_edit_schedule_entry.html', title='New Schedule Entry', form=form)

@schedule_bp.route("/copy_month_schedule", methods=["POST"])
@login_required
def copy_month_schedule():

    source_year = int(request.form.get("source_year"))
    source_month = int(request.form.get("source_month"))
    target_year = int(request.form.get("target_year"))
    target_month = int(request.form.get("target_month"))

    clear_existing = request.form.get("clear_existing") == "on"

    # -------------------------------------
    # SOURCE RANGE
    # -------------------------------------
    source_start = date(source_year, source_month, 1)
    source_end = date(
        source_year,
        source_month,
        calendar.monthrange(source_year, source_month)[1]
    )

    source_entries = (
        ScheduleEntry.query
        .join(TeamMember)
        .join(Team)
        .filter(
            Team.store_id == current_user.store_id,
            ScheduleEntry.date >= source_start,
            ScheduleEntry.date <= source_end
        )
        .all()
    )

    if not source_entries:
        flash("No schedules found in source month.", "warning")
        return redirect(url_for("schedule.schedule_calendar"))

    # -------------------------------------
    # BUILD WEEKDAY PATTERN (SKIP OFF)
    # -------------------------------------
    pattern = {}

    for entry in source_entries:

        if entry.schedule_type == "OFF":
            continue  # ✅ Skip days off automatically

        key = (entry.team_member_id, entry.date.weekday())

        # Only need one pattern per weekday
        if key not in pattern:
            pattern[key] = {
                "start_time": entry.start_time,
                "end_time": entry.end_time,
                "lunch_start": entry.lunch_start,
                "lunch_end": entry.lunch_end,
                "schedule_type": entry.schedule_type,
                "notes": entry.notes
            }

    # -------------------------------------
    # TARGET RANGE
    # -------------------------------------
    target_start = date(target_year, target_month, 1)
    target_end = date(
        target_year,
        target_month,
        calendar.monthrange(target_year, target_month)[1]
    )

    # -------------------------------------
    # CLEAR EXISTING IF REQUESTED
    # -------------------------------------
    if clear_existing:
        ScheduleEntry.query.join(TeamMember).join(Team).filter(
            Team.store_id == current_user.store_id,
            ScheduleEntry.date >= target_start,
            ScheduleEntry.date <= target_end
        ).delete(synchronize_session=False)

    # -------------------------------------
    # BUILD TARGET MONTH
    # -------------------------------------
    created = 0
    total_days = calendar.monthrange(target_year, target_month)[1]

    for day in range(1, total_days + 1):

        current_date = date(target_year, target_month, day)
        weekday = current_date.weekday()

        for (team_member_id, pattern_weekday), values in pattern.items():

            if weekday != pattern_weekday:
                continue

            # Skip if not clearing and already exists
            if not clear_existing:
                existing = ScheduleEntry.query.filter_by(
                    team_member_id=team_member_id,
                    date=current_date
                ).first()

                if existing:
                    continue

            new_entry = ScheduleEntry(
                team_member_id=team_member_id,
                date=current_date,
                start_time=values["start_time"],
                end_time=values["end_time"],
                lunch_start=values["lunch_start"],
                lunch_end=values["lunch_end"],
                schedule_type=values["schedule_type"],
                notes=values["notes"]
            )

            db.session.add(new_entry)
            created += 1

    db.session.commit()

    flash(f"Schedule copied successfully. {created} entries created.", "success")

    return redirect(url_for("schedule.schedule_calendar"))

@schedule_bp.route("/schedule/<int:entry_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_schedule_entry(entry_id):
    store_id = current_user.store_id
    entry = ScheduleEntry.query.get_or_404(entry_id)
    form = ScheduleEntryForm(obj=entry)
    # Populate choices for QuerySelectField manually
    form.team_member.choices = get_team_member_choices(store_id)

    if form.validate_on_submit():
        # QuerySelectField returns model object, manually set ID
        entry.team_member_id = form.team_member.data.id if form.team_member.data else None

        # Populate matching fields
        entry.date = form.date.data
        entry.start_time = form.start_time.data
        entry.end_time = form.end_time.data
        entry.lunch_start = form.lunch_start.data
        entry.lunch_end = form.lunch_end.data
        entry.notes = form.notes.data

        # --- NEW LOGIC: Save the Schedule Type ---
        entry.schedule_type = form.schedule_type.data
        # ----------------------------------------

        db.session.commit()
        flash('Schedule entry updated successfully!', 'success')
        return redirect(url_for('schedule.schedules'))

    return render_template('create_edit_schedule_entry.html', title='Edit Schedule Entry', form=form)

@schedule_bp.route("/schedule/<int:entry_id>/delete", methods=['POST'])
@login_required
def delete_schedule_entry(entry_id):
    entry = ScheduleEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash('Schedule entry deleted successfully!', 'success')
    return redirect(url_for('schedule.schedules'))

@schedule_bp.route("/team_schedules")
@login_required
def team_schedules():
    all_team_schedules = TeamSchedule.query.options(
        joinedload(TeamSchedule.team)
    ).order_by(TeamSchedule.team_id, TeamSchedule.day_of_week).all()
    return render_template('team_schedules.html',
                             title='Team Schedules',
                             team_schedules=all_team_schedules)

@schedule_bp.route("/team_schedule/new", methods=['GET', 'POST'])
@login_required
def new_team_schedule():
    form = TeamScheduleForm()
    if form.validate_on_submit():
        schedule = TeamSchedule()
        form.populate_obj(schedule)
        schedule.team = form.team.data
        db.session.add(schedule)
        db.session.commit()
        flash('Team schedule created successfully!', 'success')
        return redirect(url_for('schedule.team_schedules'))
    return render_template('create_edit_team_schedule.html', title='New Team Schedule', form=form)

@schedule_bp.route("/team_schedule/<int:schedule_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_team_schedule(schedule_id):
    schedule = TeamSchedule.query.get_or_404(schedule_id)
    form = TeamScheduleForm(obj=schedule)
    if form.validate_on_submit():
        form.populate_obj(schedule)
        schedule.team = form.team.data
        db.session.commit()
        flash('Team schedule updated successfully!', 'success')
        return redirect(url_for('schedule.team_schedules'))
    return render_template('create_edit_team_schedule.html', title='Edit Team Schedule', form=form)

@schedule_bp.route("/team_schedule/<int:schedule_id>/delete", methods=['POST'])
@login_required
def delete_team_schedule(schedule_id):
    schedule = TeamSchedule.query.get_or_404(schedule_id)
    db.session.delete(schedule)
    db.session.commit()
    flash('Team schedule deleted successfully!', 'success')
    return redirect(url_for('schedule.team_schedules'))

@schedule_bp.route("/generate_schedule", methods=['GET', 'POST'])
@login_required
def generate_schedule():
    form = RecurringScheduleForm()
    created_schedules = None

    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        days_of_week = form.days_of_week.data

        # Determine the year range for holiday calculation
        start_year = start_date.year
        end_year = end_date.year

        # Calculate holiday dates for the period
        holidays_in_period = set()
        for year in range(start_year, end_year + 1):
            # We only need to check the months covered by the start/end date
            start_month = start_date.month if year == start_year else 1
            end_month = end_date.month if year == end_year else 12

            for month in range(start_month, end_month + 1):
                 # Pass the month range to the helper
                holidays_in_period.update(get_holiday_dates(year, month, month))

        team_members_to_schedule = []
        flash_message_target = ""

        if form.team_member.data:
            member = TeamMember.query.options(joinedload(TeamMember.team)).get(form.team_member.data.id)
            if member:
                team_members_to_schedule.append(member)
                flash_message_target = member.name
        elif form.team.data:
            selected_team = Team.query.options(joinedload(Team.members)).get(form.team.data.id)
            if selected_team:
                team_members_to_schedule = selected_team.members
                flash_message_target = selected_team.name
        else:
            flash('You must select either a team or a team member.', 'danger')
            return render_template('generate_schedules.html', title='Generate Schedule', form=form)

        member_ids = [m.id for m in team_members_to_schedule]

        existing_schedules = ScheduleEntry.query.filter(
            ScheduleEntry.team_member_id.in_(member_ids),
            ScheduleEntry.date >= start_date,
            ScheduleEntry.date <= end_date
        ).all()

        existing_set = {(entry.team_member_id, entry.date) for entry in existing_schedules}

        new_entries_to_add = []
        current_date = start_date

        while current_date <= end_date:
            current_weekday_int = current_date.weekday()
            day_is_selected = current_weekday_int in days_of_week
            is_holiday = current_date in holidays_in_period # Check against calculated holidays

            if day_is_selected:
                for member in team_members_to_schedule:
                    if (member.id, current_date) not in existing_set:

                        # Set default schedule type based on holiday status
                        schedule_type_val = 'HOLIDAY' if is_holiday else 'WORK'

                        new_entry = ScheduleEntry(
                            team_member_id=member.id,
                            date=current_date,
                            # Clear times if it's a holiday
                            start_time=form.start_time.data if not is_holiday else None,
                            end_time=form.end_time.data if not is_holiday else None,
                            lunch_start=form.lunch_start.data if not is_holiday else None,
                            lunch_end=form.lunch_end.data if not is_holiday else None,
                            notes=form.notes.data if not is_holiday else "Shop Holiday",
                            schedule_type=schedule_type_val # Set HOLIDAY or WORK
                        )
                        new_entries_to_add.append(new_entry)

            current_date += timedelta(days=1)

        if new_entries_to_add:
            db.session.add_all(new_entries_to_add)
            db.session.commit()
            flash(f'Schedules for {flash_message_target} generated successfully!', 'success')
        else:
            flash(f'No new schedules needed for {flash_message_target} in that range.', 'info')

        created_schedules = ScheduleEntry.query.options(
            joinedload(ScheduleEntry.team_member)
        ).filter(
            ScheduleEntry.team_member_id.in_(member_ids),
            ScheduleEntry.date >= start_date,
            ScheduleEntry.date <= end_date
        ).order_by(ScheduleEntry.date, ScheduleEntry.team_member_id).all()

    return render_template('generate_schedules.html',
                             title='Generate Schedule',
                             form=form,
                             created_schedules=created_schedules)

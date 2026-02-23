from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user, AnonymousUserMixin
from extensions import db
from models import RepairOrder, WorkLog, TeamMember, ScheduleEntry, FinancialForecast, FinancialInputs, Team
from sqlalchemy import func
from datetime import date, datetime, timedelta
import calendar

main_bp = Blueprint('main', __name__)

@main_bp.route("/help")
@login_required
def help_page():
    return render_template('help.html', title='User Manual')

@main_bp.route("/")
@main_bp.route("/home")
@login_required
def home():
    user = current_user._get_current_object()

    # Operators go to operator dashboard
    if user.is_operator:
        return redirect(url_for("operator.store_index"))

    # Store users MUST have a store_id
    if not hasattr(user, "store_id"):
        return redirect(url_for("auth.login"))

    store_id = user.store_id
    today = date.today()
    now = datetime.now()


    # --- 1. FINANCIAL SCOREBOARD ---

    # Forecast & Goal
    forecast = FinancialForecast.query.filter_by(
        store_id=store_id, month=today.month, year=today.year
    ).first()

    projected_gross = forecast.total_gross if forecast else 0.0
    monthly_frh_goal = forecast.expected_frh if forecast else 0.0

    # Work Days & Progress
    _, days_in_month = calendar.monthrange(today.year, today.month)
    total_work_days = 0
    days_passed_work = 0

    for d in range(1, days_in_month + 1):
        current_d = date(today.year, today.month, d)
        if current_d.weekday() < 6: # Mon-Sat (Exclude Sunday)
            total_work_days += 1
            if d <= today.day:
                days_passed_work += 1

    work_progress_pct = (days_passed_work / total_work_days) if total_work_days > 0 else 0
    expected_pace_hours = monthly_frh_goal * work_progress_pct

    # Inputs & Shop Stats
    fin_inputs = FinancialInputs.query.filter_by(user_id=current_user.id).first()

    # --- BAY UTILIZATION CALCULATION ---
    bay_utilization = 0.0
    if fin_inputs:
        total_bays = (fin_inputs.bays_with_lifts or 0) + (fin_inputs.bays_without_lifts or 0)
        if total_bays > 0 and total_work_days > 0:
            # Capacity = Bays * 8 hours * Work Days
            shop_monthly_capacity = total_bays * 8 * total_work_days

            # Utilization = Scheduled Goal / Capacity
            # (Using monthly_frh_goal ensures we measure against what we PLAN to do)
            if shop_monthly_capacity > 0:
                bay_utilization = (monthly_frh_goal / shop_monthly_capacity) * 100
    # -----------------------------------

    # Shop Efficiency & Hours Per RO
    start_month = date(today.year, today.month, 1)
    efficiency_stats = db.session.query(
        func.sum(WorkLog.flat_rate_hours),
        func.sum(WorkLog.actual_time),
        func.count(func.distinct(WorkLog.ro_number))
    ).join(TeamMember).join(Team).filter(
        Team.store_id == store_id,
        WorkLog.date >= start_month,
        WorkLog.date <= today
    ).first()

    mtd_sold = efficiency_stats[0] or 0.0
    mtd_actual = efficiency_stats[1] or 0.0
    mtd_ro_count = efficiency_stats[2] or 0

    shop_efficiency = (mtd_sold / mtd_actual * 100) if mtd_actual > 0 else 0.0
    hours_per_ro = (mtd_sold / mtd_ro_count) if mtd_ro_count > 0 else 0.0

    # --- 2. WORKFLOW PULSE ---
    active_ros = RepairOrder.query.filter(
        RepairOrder.store_id == store_id,
        RepairOrder.status != 'Closed'
    ).all()

    status_counts = {
        'Dispatch': 0, 'Inspection': 0, 'Approval': 0,
        'Parts': 0, 'Service': 0, 'Warranty': 0, 'Ready': 0
    }
    late_ros = []
    warning_ros = []

    for ro in active_ros:
        if ro.status in status_counts:
            status_counts[ro.status] += 1
        elif ro.status == 'Warranty / Wash':
             status_counts['Warranty'] += 1

        if ro.promised_time:
            if ro.promised_time < now:
                late_ros.append(ro)
            elif ro.promised_time <= now + timedelta(hours=2):
                warning_ros.append(ro)

    late_ros.sort(key=lambda x: x.promised_time)
    warning_ros.sort(key=lambda x: x.promised_time)

    # --- 3. PRODUCTION (TODAY) ---
    today_production = db.session.query(func.sum(WorkLog.flat_rate_hours)).join(TeamMember).join(Team).filter(
        Team.store_id == store_id,
        WorkLog.date == today
    ).scalar() or 0.0

    all_techs = TeamMember.query.join(Team).filter(Team.store_id == store_id).all()
    daily_goal = 0.0
    absent_techs = []

    for tech in all_techs:
        entry = ScheduleEntry.query.filter_by(team_member_id=tech.id, date=today).first()
        if entry:
            if entry.schedule_type == 'WORK':
                if hasattr(tech, 'dpo_calculation_mode') and tech.dpo_calculation_mode == 'calculated':
                    daily_goal += tech.calculated_dpo
                else:
                    daily_goal += (tech.daily_production_objective or 0.0)
            else:
                absent_techs.append({'name': tech.name, 'reason': entry.schedule_type})

    prod_pace = (today_production / daily_goal * 100) if daily_goal > 0 else 0.0

    # --- 4. TOP PERFORMERS ---
    top_techs = db.session.query(
        TeamMember.name,
        func.sum(WorkLog.flat_rate_hours).label('total_hours')
    ).join(WorkLog).join(Team).filter(
        Team.store_id == store_id,
        WorkLog.date >= start_month,
        WorkLog.date <= today
    ).group_by(TeamMember.id).order_by(func.sum(WorkLog.flat_rate_hours).desc()).limit(5).all()

    return render_template('home.html',
                           title='Executive Dashboard',
                           today_date=today.strftime('%A, %B %d'),
                           projected_gross=projected_gross,
                           expected_pace_hours=expected_pace_hours,
                           monthly_frh_goal=monthly_frh_goal,
                           mtd_sold=mtd_sold,
                           month_progress=work_progress_pct * 100,
                           hours_per_ro=hours_per_ro,

                           # New Bay Utilization Metric
                           bay_utilization=bay_utilization,

                           shop_efficiency=shop_efficiency,
                           status_counts=status_counts,
                           late_ros=late_ros,
                           warning_ros=warning_ros,
                           today_production=today_production,
                           daily_goal=daily_goal,
                           prod_pace=prod_pace,
                           absent_techs=absent_techs,
                           top_techs=top_techs)

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user, AnonymousUserMixin
from extensions import db
from models import RepairOrder, WorkLog, TeamMember, ScheduleEntry, FinancialForecast, FinancialInputs, Team, ManagedStore
from sqlalchemy import func
from datetime import date, datetime, timedelta
import calendar
import pytz

main_bp = Blueprint('main', __name__)

#---helper elapsed work hours--
def get_elapsed_work_hours():
    tz = pytz.timezone("US/Pacific")
    now = datetime.now(tz)

    start = now.replace(hour=7, minute=0, second=0, microsecond=0)
    end = now.replace(hour=17, minute=0, second=0, microsecond=0)

    if now < start:
        return 0.1  # prevents divide-by-zero + early morning weirdness

    if now > end:
        return 10  # full day

    elapsed = now - start
    return elapsed.total_seconds() / 3600

#---Todays Focus helper---
import math

def generate_today_focus(daily_goal, today_production, forecasted_utilization, current_utilization, status_counts):
    gap = max(daily_goal - today_production, 0)
    ros_needed = math.ceil(gap / 2) if gap > 0 else 0  # ~2 FRH per RO

    if gap <= 0:
        return {
            "issue": "On Track",
            "blocker": "None",
            "gap": 0,
            "ros_needed": 0,
            "pace_needed": 0,
            "actions": [
                "Maintain current workflow",
                "Keep dispatch flowing",
                "Watch carryover"
            ],
            "message": "You are on pace for today",

            # 🔥 REQUIRED (prevents crash)
            "utilization_hint": "",
            "recovery_target": 0,
            "recovery_ros": 0,
            "dispatch_pull": 0,
            "inspection_pull": 0,
            "approval_pull": 0
        }

    if today_production == 0:
        issue = "No Production Started"
        blocker = "No active work in process"
        actions = [
            "Dispatch first jobs immediately",
            "Check for stuck write-ups or approvals",
            "Load bays with quick work first"
        ]
    elif current_utilization < forecasted_utilization:
        issue = "Low Utilization"
        blocker = "Workload lacking"
        actions = [
            "Pull forward appointments",
            "Call waiters / no-shows",
            "Rebalance advisor load"
        ]
    else:
        issue = "Pacing Risk"
        actions = [
            "Prioritize quick-turn jobs",
            "Close near-complete ROs",
            "Push approvals"
        ]

    # simple pacing (we'll upgrade later)
    elapsed_hours = get_elapsed_work_hours()
    remaining_hours = max(10 - get_elapsed_work_hours(), 1)

    pace_needed = round(gap / remaining_hours, 1)

   
    # convert to 2-hour recovery block
    recovery_hours = min(2, remaining_hours)
    recovery_target = round(pace_needed * recovery_hours, 1)

    # convert to ROs (~2 FRH each)
    recovery_ros = int(recovery_target / 2)

    
    dispatch = status_counts.get('Dispatch', 0)
    inspection = status_counts.get('Inspection', 0)
    approval = status_counts.get('Approval', 0)
    service = status_counts.get('Service', 0)
    dispatch_pull = min(dispatch, int(recovery_ros * 0.5))
    inspection_pull = min(inspection, int(recovery_ros * 0.3))
    approval_pull = min(approval, int(recovery_ros * 0.2))
    production_ratio = 0

    if daily_goal > 0:
        production_ratio = today_production / daily_goal

    # 🚨 1. NOTHING IN SERVICE (CRITICAL)
    if service == 0 and dispatch > 0:
        issue = "No Active Work"
        blocker = f"{dispatch} ROs ready but none in service"
        actions = [
            "Assign work to techs immediately",
            "Move top priority ROs into service",
            "Verify techs are actively working"
        ]

    # 🚧 2. STUCK BEFORE INSPECTION
    elif dispatch > 0 and inspection == 0:
        issue = "Dispatch Bottleneck"
        blocker = f"{dispatch} ROs not entering inspection"
        actions = [
            "Start inspections immediately",
            "Assign diagnostic work",
            "Ensure techs are pulling vehicles in"
        ]

    # 🔍 3. INSPECTION BACKLOG
    elif inspection > service * 2:
        issue = "Inspection Backlog"
        blocker = f"{inspection} ROs stuck in inspection"
        actions = [
            "Complete diagnostics faster",
            "Move completed inspections to approval",
            "Prioritize quick inspections"
        ]

    # 📞 4. APPROVAL BOTTLENECK
    elif approval > service:
        issue = "Approval Bottleneck"
        blocker = f"{approval} ROs waiting for approval"
        actions = [
            "Call customers immediately",
            "Prioritize high-value approvals",
            "Clear approval queue"
        ]

    # ⚖️ 5. SERVICE UNDERLOADED
    elif service < dispatch:
        issue = "Underloaded Service"
        blocker = f"Only {service} active vs {dispatch} ready"
        actions = [
            "Increase dispatch rate",
            "Feed more work into service",
            "Balance workload across techs"
        ]

    # 📉 6. UTILIZATION PROBLEM (only if flow exists)
    elif current_utilization < forecasted_utilization:
        issue = "Low Utilization"
        blocker = "Not enough work loaded"
        actions = [
            "Pull forward appointments",
            "Call waiters / no-shows",
            "Increase incoming work"
        ]

    elif production_ratio < 0.5 and service > 0:
        issue = "Low Production Output"
        blocker = f"Only {round(production_ratio * 100)}% of target achieved - Low Technician Output"
        actions = [
            "Check technician productivity",
            "Intervene with slow and/or idle techs",
            "Prioritize high-hour jobs"
        ]

    # 🟢 DEFAULT
    else:
        issue = "Pacing Risk"
        blocker = "Behind expected output"
        actions = [
            "Push quick-turn work",
            "Close near-complete ROs",
            "Reduce downtime"
        ]
    utilization_hint = ""

    if service == 0 and dispatch > 20:
        utilization_hint = "⚠️ High idle capacity detected"
    
    
       

    return {
        "issue": issue,
        "blocker": blocker,
        "actions": actions,
        "gap": round(gap, 1),
        "ros_needed": ros_needed,
        "pace_needed": pace_needed,
        "message": f"You are behind by {round(gap, 1)} FRH",
        "utilization_hint": utilization_hint,
        "recovery_target": recovery_target,
        "recovery_ros": recovery_ros,
        "dispatch_pull": dispatch_pull,
        "inspection_pull": inspection_pull,
        "approval_pull": approval_pull
            }

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
    hours_per_ro = (mtd_sold / mtd_ro_count) if mtd_ro_count > 0 else 0

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

    #todays gross target ---
    today_labor_gross = 0
    today_parts_gross = 0
    today_total_gross = 0

    fin_inputs = FinancialInputs.query.filter_by(user_id=current_user.id).first()

    if fin_inputs and daily_goal > 0:

        elr = fin_inputs.effective_labor_rate or 0
        parts_ratio = fin_inputs.parts_to_labor_ratio or 0
        labor_margin = (fin_inputs.labor_margin or 0) / 100
        parts_margin = (fin_inputs.parts_margin or 0) / 100

        # Revenue
        labor_revenue = daily_goal * elr
        parts_revenue = labor_revenue * parts_ratio

        # Gross
        today_labor_gross = labor_revenue * labor_margin
        today_parts_gross = parts_revenue * parts_margin
        today_total_gross = today_labor_gross + today_parts_gross

    # --- Needed Appointments Calculation (AFTER daily_goal exists) ---

    needed_appointments = 0

    if hours_per_ro > 0 and daily_goal > 0:
        needed_appointments = round(daily_goal / hours_per_ro)

    cp_needed = round(needed_appointments * 0.70)
    wp_needed = needed_appointments - cp_needed

    prod_pace = (today_production / daily_goal * 100) if daily_goal > 0 else 0.0

    #--todays needed hours--
    needed_today_hours = daily_goal
    remaining_today_hours = max(daily_goal - today_production, 0)

    # --- Monthly Planned UTILIZATION CALCULATION ---
    projected_eod = 0
    total_bays = 0


    # --- Monthly Planned UTILIZATION ---
    monthly_planned_utilization = 0.0

    if fin_inputs:
        total_bays = (fin_inputs.bays_with_lifts or 0) + (fin_inputs.bays_without_lifts or 0)
        
        if total_bays > 0 and total_work_days > 0:
            shop_monthly_capacity = total_bays * 8 * total_work_days

            if shop_monthly_capacity > 0:
                monthly_planned_utilization = (monthly_frh_goal / shop_monthly_capacity) * 100

    #---mtd utilization ---
    mtd_utilization = 0

    if total_bays > 0 and days_passed_work > 0:
        mtd_capacity = total_bays * 8 * days_passed_work
        if mtd_capacity > 0:
            mtd_utilization = (mtd_sold / mtd_capacity) * 100

    mtd_utilization = round(mtd_utilization, 1)

    # --- Daily Capacity ---
    bay_daily_capacity = total_bays * 8 if total_bays > 0 else 0


    # --- Projected EOD (LIVE PACE - KEEP THIS) ---
    elapsed_hours = get_elapsed_work_hours()
    total_work_hours = 10  # FIXED (you had 9 but your day is 7–17)

    if elapsed_hours > 0:
        projected_eod = (today_production / elapsed_hours) * total_work_hours

    projected_eod = max(projected_eod, 0)


    # --- Forecast vs Actual (THIS IS THE KEY CHANGE) ---
    forecasted_hours_today = daily_goal
    current_hours_today = today_production


    # --- Forecasted Utilization (PLAN-BASED, NOT PACE) ---
    forecasted_utilization = 0

    if bay_daily_capacity > 0:
        forecasted_utilization = (forecasted_hours_today / bay_daily_capacity) * 100

    forecasted_utilization = min(round(forecasted_utilization, 1), 150)


    # --- Current Utilization ---
    current_utilization = 0

    if bay_daily_capacity > 0:
        current_utilization = (current_hours_today / bay_daily_capacity) * 100

    current_utilization = min(round(current_utilization, 1), 150)


    # --- Capacity GAP (VS PLAN, NOT BUILDING) ---
    capacity_gap_hours = round(forecasted_hours_today - current_hours_today, 1)
    capacity_gap_hours = max(capacity_gap_hours, 0)


    # --- Gap % (VS PLAN) ---
    capacity_gap_pct = 0

    if forecasted_hours_today > 0:
        capacity_gap_pct = round((capacity_gap_hours / forecasted_hours_today) * 100, 1)


    # --- Plan Comparison ---
    utilization_vs_plan = round(forecasted_utilization - monthly_planned_utilization, 1)

    # --- 4. TOP/bottom PERFORMERS ---
    top_techs = db.session.query(
        TeamMember.name,
        func.sum(WorkLog.flat_rate_hours).label('total_hours')
    ).join(WorkLog).join(Team).filter(
        Team.store_id == store_id,
        WorkLog.date >= start_month,
        WorkLog.date <= today
    ).group_by(TeamMember.id).order_by(func.sum(WorkLog.flat_rate_hours).desc()).limit(5).all()

    bottom_techs = db.session.query(
        TeamMember.name,
        func.sum(WorkLog.flat_rate_hours).label('total_hours')
    ).join(WorkLog).join(Team).filter(
        Team.store_id == store_id,
        WorkLog.date >= start_month,
        WorkLog.date <= today
    ).group_by(TeamMember.id).order_by(func.sum(WorkLog.flat_rate_hours).asc()).limit(5).all()
        # --- 5. WEEKLY FINANCIAL FORECAST (for Executive Dashboard) ---

    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    current_week_dates = f"{start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d')}"

    weekly_financial_total = {
        "total_gross": 0.0,
        "labor_gross": 0.0,
        "parts_gross": 0.0,
        "expected_frh": 0.0
    }

    # Pull forecast for the month
    forecast = FinancialForecast.query.filter_by(
        store_id=store_id,
        month=today.month,
        year=today.year
    ).first()

    if forecast:
        # Estimate weekly portion from monthly totals
        weekly_financial_total["total_gross"] = forecast.total_gross / 4
        weekly_financial_total["labor_gross"] = forecast.labor_gross / 4
        weekly_financial_total["parts_gross"] = forecast.parts_gross / 4
        weekly_financial_total["expected_frh"] = forecast.expected_frh / 4
    
    store = db.session.get(ManagedStore, store_id)

    routesheet_audit = store.routesheet_audit_timestamp if store else None
    tech_hours_audit = store.tech_hours_audit_timestamp if store else None

    routesheet_audit_stale = True
    tech_hours_audit_stale = True

    pacific = pytz.timezone("US/Pacific")

    if routesheet_audit:
        routesheet_audit_stale = datetime.utcnow() - routesheet_audit > timedelta(hours=24)

    if tech_hours_audit:
        tech_hours_audit_stale = datetime.utcnow() - tech_hours_audit > timedelta(hours=24)
   
    # --- Today's Needed Hours to Stay on Pace ---

    remaining_work_days = total_work_days - days_passed_work

    today_needed_hours = 0

    if remaining_work_days > 0:
        today_needed_hours = ((expected_pace_hours - mtd_sold) / remaining_work_days) + daily_goal

    today_needed_hours = max(today_needed_hours, 0)

    today_focus = generate_today_focus(
        daily_goal,
        today_production,
        forecasted_utilization,
        current_utilization,
        status_counts
    )

    critical_ros = late_ros[:5]
    remaining_late_count = max(len(late_ros) - 5, 0)

    return render_template('home.html',
                           title='Executive Dashboard',
                           today_date=today.strftime('%A, %B %d'),
                           today_total_gross=today_total_gross,
                           today_labor_gross=today_labor_gross,
                           today_parts_gross=today_parts_gross,
                           projected_gross=projected_gross,
                           expected_pace_hours=expected_pace_hours,
                           monthly_frh_goal=monthly_frh_goal,
                           mtd_sold=mtd_sold,
                           month_progress=work_progress_pct * 100,
                           hours_per_ro=hours_per_ro,
                           weekly_financial_total=weekly_financial_total,
                           current_week_dates=current_week_dates,
                           needed_appointments=needed_appointments,
                           cp_needed=cp_needed,
                           wp_needed=wp_needed,
                           routesheet_audit=routesheet_audit,
                           tech_hours_audit=tech_hours_audit,
                           routesheet_audit_stale=routesheet_audit_stale,
                           tech_hours_audit_stale=tech_hours_audit_stale,
                           today_needed_hours=today_needed_hours,


                           # New Bay Utilization Metric
                           mtd_utilization=mtd_utilization,
                           monthly_planned_utilization=monthly_planned_utilization,
                           current_utilization=current_utilization,
                           forecasted_utilization=forecasted_utilization,
                           capacity_gap_hours=capacity_gap_hours,
                           utilization_vs_plan=utilization_vs_plan,
                           projected_eod=projected_eod,
                           shop_efficiency=shop_efficiency,
                           status_counts=status_counts,
                           critical_ros=critical_ros,
                           remaining_late_count=remaining_late_count,
                           warning_ros=warning_ros,
                           today_production=today_production,
                           daily_goal=daily_goal,
                           prod_pace=prod_pace,
                           absent_techs=absent_techs,
                           top_techs=top_techs,
                           bottom_techs=bottom_techs,
                           today_focus=today_focus,
                           needed_today_hours=needed_today_hours,
                           remaining_today_hours=remaining_today_hours
                           )

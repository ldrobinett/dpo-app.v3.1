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
    is_working_day = today.weekday() < 6
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
    mtd_pace_delta = mtd_sold - expected_pace_hours
    if mtd_pace_delta < -0.1 * monthly_frh_goal:
        mtd_status = "🔴 Off Track"
    elif mtd_pace_delta < 0:
        mtd_status = "🟡 Slightly Behind"
    else:
        mtd_status = "🟢 On Track"

    mtd_status_detail = f"Behind MTD Pace by {abs(int(mtd_pace_delta))} hrs"

    # --- TREND DIRECTION (LAST 3 WORK DAYS VS PRIOR) ---

    recent_days = []
    prior_days = []

    # Get last 6 working days (excluding Sundays)
    d = today
    while len(recent_days) + len(prior_days) < 6:
        if d.weekday() < 6:  # Mon-Sat
            day_hours = db.session.query(func.sum(WorkLog.flat_rate_hours)).join(TeamMember).join(Team).filter(
                Team.store_id == store_id,
                WorkLog.date == d
            ).scalar() or 0.0

            if len(recent_days) < 3:
                recent_days.append(day_hours)
            else:
                prior_days.append(day_hours)

        d -= timedelta(days=1)

    # Averages
    recent_avg = sum(recent_days) / len(recent_days) if recent_days else 0
    prior_avg = sum(prior_days) / len(prior_days) if prior_days else 0

    trend = "Stable"
    trend_icon = "⚪"

    if prior_avg > 0:
        change_ratio = (recent_avg - prior_avg) / prior_avg

        if change_ratio > 0.1:
            trend = "Improving"
            trend_icon = "🟢"
        elif change_ratio < -0.1:
            trend = "Declining"
            trend_icon = "🔴"
        else:
            trend = "Stable"
            trend_icon = "🟡"

    # --- MTD RECOVERY MODEL ---
    remaining_work_days = total_work_days - days_passed_work

    remaining_hours_needed = max(monthly_frh_goal - mtd_sold, 0)

    required_daily_recovery = 0
    recovery_status = "On Track"

    if remaining_work_days > 0:
        required_daily_recovery = remaining_hours_needed / remaining_work_days

    # Compare against current daily goal (real capacity signal)
    if daily_goal > 0:
        if required_daily_recovery > daily_goal * 1.2:
            recovery_status = "🔴 Unrealistic Recovery"
        elif required_daily_recovery > daily_goal:
            recovery_status = "🟡 Aggressive Recovery"
        else:
            recovery_status = "🟢 Achievable"

    required_daily_recovery = round(required_daily_recovery, 1)
    remaining_hours_needed = round(remaining_hours_needed, 1)
        recovery_ros_per_day = 0

    if hours_per_ro > 0:
        recovery_ros_per_day = round(required_daily_recovery / hours_per_ro)

    # --- PROJECTED MONTH-END OUTCOME ---

    projected_month_end = 0
    projection_delta = 0
    projection_status = "On Track"

    if days_passed_work > 0:
        avg_daily_output = mtd_sold / days_passed_work
        projected_month_end = avg_daily_output * total_work_days

    projection_delta = projected_month_end - monthly_frh_goal

    # Status based on projection (this is the REAL truth)
    if projection_delta < -0.1 * monthly_frh_goal:
        projection_status = "🔴 Will Miss Target"
    elif projection_delta < 0:
        projection_status = "🟡 Slightly Under Target"
    else:
        projection_status = "🟢 On Track to Hit Target"

    projected_month_end = round(projected_month_end, 1)
    projection_delta = round(projection_delta, 1)
    # --- PROJECTION CONFIDENCE MODEL ---

    confidence_level = "Medium"
    confidence_score = 0

    # 1. Gap severity (how far off target)
    gap_ratio = 0
    if monthly_frh_goal > 0:
        gap_ratio = abs(projection_delta) / monthly_frh_goal

    # 2. Recovery pressure (how hard it is to fix)
    recovery_pressure = 0
    if daily_goal > 0:
        recovery_pressure = required_daily_recovery / daily_goal

    # 3. Combine into confidence score
    # Lower score = worse confidence
    confidence_score = 1.0

    # Penalize large gap
    if gap_ratio > 0.2:
        confidence_score -= 0.4
    elif gap_ratio > 0.1:
        confidence_score -= 0.2

    # Penalize unrealistic recovery
    if recovery_pressure > 1.2:
        confidence_score -= 0.4
    elif recovery_pressure > 1.0:
        confidence_score -= 0.2

    # Clamp score
    confidence_score = max(min(confidence_score, 1.0), 0.0)

    # Convert to label
    if confidence_score >= 0.75:
        confidence_level = "🟢 High Confidence"
    elif confidence_score >= 0.5:
        confidence_level = "🟡 Moderate Confidence"
    else:
        confidence_level = "🔴 Low Confidence"

    # --- EARLY WARNING SYSTEM ---

    early_warning_triggered = False
    early_warning_level = "None"
    early_warning_message = ""

    # Core signals
    is_projection_bad = projection_delta < 0
    is_low_confidence = confidence_score < 0.5
    is_declining = trend == "Declining"

    # Days remaining safety check
    days_remaining = total_work_days - days_passed_work

    # 🚨 LEVEL 3: CRITICAL (Unrecoverable trajectory)
    if is_projection_bad and is_low_confidence and is_declining:
        early_warning_triggered = True
        early_warning_level = "🔴 Critical"
        early_warning_message = "Performance declining with low recovery probability"

    # ⚠️ LEVEL 2: HIGH RISK (Needs immediate correction)
    elif is_projection_bad and is_low_confidence:
        early_warning_triggered = True
        early_warning_level = "🟠 High Risk"
        early_warning_message = "Unlikely to hit target without immediate improvement"

    # ⚡ LEVEL 1: WARNING (Trend not supporting recovery)
    elif is_projection_bad and trend != "Improving":
        early_warning_triggered = True
        early_warning_level = "🟡 Warning"
        early_warning_message = "Behind plan and not improving"

    # 🧊 SAFE ZONE
    else:
        early_warning_triggered = False
        early_warning_level = "🟢 Stable"
        early_warning_message = "No immediate risk detected"

    # --- TIME PRESSURE ESCALATION ---

    if early_warning_triggered and days_remaining <= 5:
        early_warning_level = "🔴 Critical"
        early_warning_message += " (Very limited time remaining)"

    elif early_warning_triggered and days_remaining <= 10:
        early_warning_level = "🟠 High Risk"
        early_warning_message += " (Time window closing)"

    improved = False

    if trend == "Improving":
        improved = True
    elif mtd_pace_delta > -0.05 * monthly_frh_goal:
        improved = True

    # --- RECOMMENDED ACTIONS ENGINE (AUTO-PRIORITIZED) ---

    scored_actions = []

    def add_action(text, impact=1, urgency=1, bottleneck=1):
        score = (impact * 2) + (urgency * 2) + (bottleneck * 3)

        # --- ADAPTIVE LEARNING ---
        history = ActionHistory.query.filter_by(
            store_id=store_id,
            action_text=text
        ).order_by(ActionHistory.timestamp.desc()).limit(5).all()

        if history:
            success_rate = sum(1 for h in history if h.success) / len(history)

            if success_rate > 0.7:
                score += 2
            elif success_rate < 0.3:
                score -= 2

        scored_actions.append({
            "text": text,
            "score": score
        })

    # Pull workflow signals
    dispatch = status_counts.get('Dispatch', 0)
    inspection = status_counts.get('Inspection', 0)
    approval = status_counts.get('Approval', 0)
    service = status_counts.get('Service', 0)

    # --- CRITICAL LEVEL ---
    if early_warning_level == "🔴 Critical":

        if service == 0 and dispatch > 0:
            add_action("Assign work to technicians immediately", 3, 3, 3)
            add_action("Move highest value ROs into service", 3, 3, 3)
            add_action("Verify all techs are actively working", 2, 3, 2)

        elif approval > service:
            add_action("Call all pending approvals immediately", 3, 3, 3)
            add_action("Prioritize high-dollar ROs", 2, 3, 2)

        elif inspection > service * 2:
            add_action("Push inspections to completion", 3, 3, 3)
            add_action("Move completed inspections to approval", 2, 2, 3)

        else:
            add_action("Increase car count immediately", 3, 3, 2)
            add_action("Prioritize quick-turn jobs", 2, 3, 2)

    # --- HIGH RISK ---
    elif early_warning_level == "🟠 High Risk":

        if dispatch > service:
            add_action("Increase dispatch rate", 2, 2, 3)
            add_action("Ensure bays stay fully loaded", 2, 2, 2)

        elif approval > 0:
            add_action("Focus on approvals to unlock work", 2, 2, 3)

        else:
            add_action("Improve workflow efficiency", 1, 2, 1)

    # --- WARNING / STABLE ---
    else:
        add_action("Maintain steady production flow", 1, 1, 1)


    # --- RECOVERY PRESSURE BOOST ---
    if daily_goal > 0:
        if required_daily_recovery > daily_goal * 1.2:
            add_action("Add overtime or increase capacity", 3, 3, 2)
        elif required_daily_recovery > daily_goal:
            add_action("Increase output beyond normal capacity", 2, 2, 2)


    # --- SORT + LIMIT ---
    scored_actions.sort(key=lambda x: x["score"], reverse=True)

    recommended_actions = [a["text"] for a in scored_actions[:5]]
    # --- SAVE ACTION OUTCOMES (ONCE PER DAY) ---
    if now.hour >= 17:  # end-of-day snapshot

        for action in recommended_actions:
            db.session.add(ActionHistory(
                store_id=store_id,
                action_text=action,
                success=improved
            ))

        db.session.commit()

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
                           mtd_status=mtd_status,
                           mtd_status_detail=mtd_status_detail,
                           expected_pace_hours=expected_pace_hours,
                           mtd_pace_delta=mtd_pace_delta,
                           is_working_day=is_working_day,
                           required_daily_recovery=required_daily_recovery,
                           remaining_hours_needed=remaining_hours_needed,
                           recovery_status=recovery_status,
                           recovery_ros_per_day=recovery_ros_per_day,
                           projected_month_end=projected_month_end,
                           projection_delta=projection_delta,
                           projection_status=projection_status,
                           confidence_level=confidence_level,
                           confidence_score=round(confidence_score, 2),
                           trend=trend,
                           trend_icon=trend_icon,
                           recent_avg=round(recent_avg, 1),
                           prior_avg=round(prior_avg, 1),
                           early_warning_triggered=early_warning_triggered,
                           early_warning_level=early_warning_level,
                           early_warning_message=early_warning_message,
                           days_remaining=days_remaining,
                           recommended_actions=recommended_actions,        


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

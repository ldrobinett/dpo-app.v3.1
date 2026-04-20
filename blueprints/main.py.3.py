from operator import or_

from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from extensions import db
from models import (
    RepairOrder,
    WorkLog,
    TeamMember,
    ScheduleEntry,
    FinancialForecast,
    FinancialInputs,
    Team,
    ManagedStore,
    ActionHistory,
    DecisionWeights,
    DailyMetrics  # requires model in models.py
)
from sqlalchemy import func, case
from datetime import date, datetime, timedelta
import calendar
import pytz
import math
import random

main_bp = Blueprint("main", __name__)


# =========================================================
# HELPERS
# =========================================================
def get_priority_label(score: float) -> str:
    if score >= 15:
        return "High"
    elif score >= 8:
        return "Medium"
    return "Low"

def get_elapsed_work_hours():
    tz = pytz.timezone("US/Pacific")
    now = datetime.now(tz)

    start = now.replace(hour=7, minute=0, second=0, microsecond=0)
    end = now.replace(hour=17, minute=0, second=0, microsecond=0)

    if now < start:
        return 0.1  # prevent divide-by-zero early AM
    if now > end:
        return 10.0  # full day elapsed

    elapsed = now - start
    return elapsed.total_seconds() / 3600

def count_workdays(start_date, end_date):
    day_count = 0
    current = start_date

    while current <= end_date:
        if current.weekday() != 6:  # 6 = Sunday
            day_count += 1
        current += timedelta(days=1)

    return day_count

def generate_today_focus(
    daily_goal,
    today_production,
    forecasted_utilization,
    current_utilization,
    status_counts,
):
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
                "Watch carryover",
            ],
            "message": "You are on pace for today",
            "utilization_hint": "",
            "recovery_target": 0,
            "recovery_ros": 0,
            "dispatch_pull": 0,
            "inspection_pull": 0,
            "approval_pull": 0,
        }

    if today_production == 0:
        issue = "No Production Started"
        blocker = "No active work in process"
        actions = [
            "Dispatch first jobs immediately",
            "Check for stuck write-ups or approvals",
            "Load bays with quick work first",
        ]
    elif current_utilization < forecasted_utilization:
        issue = "Low Utilization"
        blocker = "Workload lacking"
        actions = [
            "Pull forward appointments",
            "Call waiters / no-shows",
            "Rebalance advisor load",
        ]
    else:
        issue = "Pacing Risk"
        blocker = "Behind expected output"
        actions = [
            "Prioritize quick-turn jobs",
            "Close near-complete ROs",
            "Push approvals",
        ]

    remaining_hours = max(10 - get_elapsed_work_hours(), 1)
    pace_needed = round(gap / remaining_hours, 1)

    recovery_hours = min(2, remaining_hours)
    recovery_target = round(pace_needed * recovery_hours, 1)
    recovery_ros = int(recovery_target / 2)

    dispatch = status_counts.get("Dispatch", 0)
    inspection = status_counts.get("Inspection", 0)
    approval = status_counts.get("Approval", 0)
    service = status_counts.get("Service", 0)

    dispatch_pull = min(dispatch, int(recovery_ros * 0.5))
    inspection_pull = min(inspection, int(recovery_ros * 0.3))
    approval_pull = min(approval, int(recovery_ros * 0.2))

    production_ratio = (today_production / daily_goal) if daily_goal > 0 else 0

    if service == 0 and dispatch > 0:
        issue = "No Active Work"
        blocker = f"{dispatch} ROs ready but none in service"
        actions = [
            "Assign work to techs immediately",
            "Move top priority ROs into service",
            "Verify techs are actively working",
        ]
    elif dispatch > 0 and inspection == 0:
        issue = "Dispatch Bottleneck"
        blocker = f"{dispatch} ROs not entering inspection"
        actions = [
            "Start inspections immediately",
            "Assign diagnostic work",
            "Ensure techs are pulling vehicles in",
        ]
    elif inspection > service * 2:
        issue = "Inspection Backlog"
        blocker = f"{inspection} ROs stuck in inspection"
        actions = [
            "Complete diagnostics faster",
            "Move completed inspections to approval",
            "Prioritize quick inspections",
        ]
    elif approval > service:
        issue = "Approval Bottleneck"
        blocker = f"{approval} ROs waiting for approval"
        actions = [
            "Call customers immediately",
            "Prioritize high-value approvals",
            "Clear approval queue",
        ]
    elif service < dispatch:
        issue = "Underloaded Service"
        blocker = f"Only {service} active vs {dispatch} ready"
        actions = [
            "Increase dispatch rate",
            "Feed more work into service",
            "Balance workload across techs",
        ]
    elif current_utilization < forecasted_utilization:
        issue = "Low Utilization"
        blocker = "Not enough work loaded"
        actions = [
            "Pull forward appointments",
            "Call waiters / no-shows",
            "Increase incoming work",
        ]
    elif production_ratio < 0.5 and service > 0:
        issue = "Low Production Output"
        blocker = (
            f"Only {round(production_ratio * 100)}% of target achieved - "
            f"Low Technician Output"
        )
        actions = [
            "Check technician productivity",
            "Intervene with slow and/or idle techs",
            "Prioritize high-hour jobs",
        ]
    else:
        issue = "Pacing Risk"
        blocker = "Behind expected output"
        actions = [
            "Push quick-turn work",
            "Close near-complete ROs",
            "Reduce downtime",
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
        "approval_pull": approval_pull,
    }


def get_action_history_success_rate(store_id, action_text, limit=5):
    history = (
        ActionHistory.query.filter_by(store_id=store_id, action_text=action_text)
        .order_by(ActionHistory.timestamp.desc())
        .limit(limit)
        .all()
    )
    if not history:
        return None #means "not data"
    return sum(1 for h in history if h.success) / len(history)

def get_context_match_score(action_text, current_context, store_id):
    history = (
        ActionHistory.query.filter_by(
            store_id=store_id,
            action_text=action_text
        )
        .order_by(ActionHistory.timestamp.desc())
        .limit(10)
        .all()
    )

    if not history:
        return 0

    total_score = 0

    for h in history:
        score = 0

        # Context similarity checks
        if h.approval_count and current_context["approval"] > current_context["service"]:
            if h.approval_count > h.service_count:
                score += 1

        if h.inspection_count and current_context["inspection"] > current_context["service"] * 1.5:
            if h.inspection_count > h.service_count * 1.5:
                score += 1

        if h.dispatch_count and current_context["dispatch"] > current_context["service"]:
            if h.dispatch_count > h.service_count:
                score += 1

        if h.success:
            score += 1

        total_score += score

    # 🔥 NORMALIZE to 0–1 range
    max_possible = len(history) * 4  # 4 max points per record
    return total_score / max_possible if max_possible else 0

def get_history_score(success_rate):
    if success_rate is None:
        return 0

    # Normalize to -1 → +1 range
    return (success_rate - 0.5) * 2

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)


def tune_decision_weights(store_id):
    weights = DecisionWeights.query.filter_by(store_id=store_id).first()
    if not weights:
        return

    recent_history = (
        ActionHistory.query.filter_by(store_id=store_id)
        .order_by(ActionHistory.timestamp.desc())
        .limit(30)
        .all()
    )

    if len(recent_history) < 10:
        return  # not enough data, calm down

    success_rate = sum(1 for h in recent_history if h.success) / len(recent_history)

    approval_cases = [h for h in recent_history if (h.approval_count or 0) > (h.service_count or 0)]
    inspection_cases = [h for h in recent_history if (h.inspection_count or 0) > ((h.service_count or 0) * 1.5)]
    dispatch_cases = [h for h in recent_history if (h.dispatch_count or 0) > (h.service_count or 0)]

    context_cases = approval_cases + inspection_cases + dispatch_cases
    context_success_rate = (
        sum(1 for h in context_cases if h.success) / len(context_cases)
        if context_cases else None
    )

    # --- slow tuning logic ---
    # if overall system is doing well, reward history slightly
    if success_rate >= 0.7:
        weights.history_weight = clamp(weights.history_weight + 0.1, 1.0, 3.0)
    elif success_rate < 0.5:
        weights.history_weight = clamp(weights.history_weight - 0.1, 1.0, 3.0)

    # if context-heavy situations are performing well, reward context
    if context_success_rate is not None:
        if context_success_rate >= 0.7:
            weights.context_weight = clamp(weights.context_weight + 0.1, 0.5, 3.0)
        elif context_success_rate < 0.5:
            weights.context_weight = clamp(weights.context_weight - 0.1, 0.5, 3.0)

    # keep base stable, but slightly stronger when adaptive signals are weak
    if success_rate < 0.5 and (context_success_rate is None or context_success_rate < 0.5):
        weights.base_weight = clamp(weights.base_weight + 0.05, 0.8, 2.0)
    else:
        weights.base_weight = clamp(weights.base_weight - 0.02, 0.8, 2.0)

    db.session.commit()

def validate_response(issue_key, response):

    if not response:
        return "missing", "No response provided"

    r = response.lower()

    rules = {
        "dispatch": ["inspect", "pull", "move", "assign", "tech"],
        "appointments": ["call", "schedule", "wait", "pull", "book"],
        "production": ["tech", "balance", "work", "dispatch", "load"]
    }

    keywords = rules.get(issue_key, [])

    if not any(k in r for k in keywords):
        return "weak", "No clear action tied to issue"

    return "good", "Valid plan"
# =========================================================
# ROUTES
# =========================================================
@main_bp.route("/help")
@login_required
def help_page():
    return render_template("help.html", title="User Manual")


@main_bp.route("/", methods=["GET", "POST"])
@main_bp.route("/home", methods=["GET", "POST"])
@login_required
def home():
    today = date.today()
    
    start_month = date(today.year, today.month, 1)
    def get_last_workday(d):
        d = d - timedelta(days=1)
        while d.weekday() == 6:  # skip Sundays
            d -= timedelta(days=1)
        return d

    metrics_date = get_last_workday(today)

    user = current_user._get_current_object()

    if user.is_operator:
        return redirect(url_for("operator.store_index"))

    if not hasattr(user, "store_id"):
        return redirect(url_for("auth.login"))

    store_id = user.store_id
    now = datetime.now()

    # =====================================================
    # 🔥 AUDIT STATUS (YOU MISSED THIS)
    # =====================================================
    store = ManagedStore.query.get(store_id)

    routesheet_audit = store.routesheet_audit_timestamp
    tech_hours_audit = store.tech_hours_audit_timestamp

    routesheet_audit_stale = True
    tech_hours_audit_stale = True

    if routesheet_audit:
        routesheet_audit_stale = (datetime.utcnow() - routesheet_audit) > timedelta(hours=2)

    if tech_hours_audit:
        tech_hours_audit_stale = (datetime.utcnow() - tech_hours_audit) > timedelta(hours=2)

    
    # =====================================================
    # 1. FORECAST
    # =====================================================
    forecast = FinancialForecast.query.filter_by(
        store_id=store_id, month=today.month, year=today.year
    ).first()

    projected_gross = forecast.total_gross if forecast else 0.0
    monthly_frh_goal = forecast.expected_frh if forecast else 0.0

    # =====================================================
    # 2. CALENDAR - does'nt count sundays uses helper function to define where we are mtd
    # =====================================================
    _, days_in_month = calendar.monthrange(today.year, today.month)
    end_of_month = date(today.year, today.month, days_in_month)

    total_work_days = count_workdays(start_month, end_of_month)
    days_passed_work = count_workdays(start_month, metrics_date)
    remaining_work_days = count_workdays(today, end_of_month)

    # =====================================================
    # 3. WORKFLOW COUNTS (FIXED)
    # =====================================================
    active_ros = RepairOrder.query.filter(
        RepairOrder.store_id == store_id,
        RepairOrder.status != "Closed",
    ).all()

    status_counts = {
        "Dispatch": 0,
        "Inspection": 0,
        "Approval": 0,
        "Parts": 0,
        "Service": 0,
        "Warranty": 0,
        "Ready": 0,
    }

    for ro in active_ros:
        if ro.status in status_counts:
            status_counts[ro.status] += 1

    # ✅ FIXED — NOW AFTER LOOP
    dispatch = status_counts.get("Dispatch", 0)
    inspection = status_counts.get("Inspection", 0)
    approval = status_counts.get("Approval", 0)
    service = status_counts.get("Service", 0)

    # =====================================================
    # 🔥 ROUTE SUMMARY (NEW)
    # =====================================================
    mtd_sold = (
        db.session.query(func.sum(WorkLog.flat_rate_hours))
        .join(TeamMember)
        .join(Team)
        .filter(
            Team.store_id == store_id,
            WorkLog.date >= start_month,
            WorkLog.date <= metrics_date,
        )
        .scalar()
        or 0.0
    )
    
    
    total_ros_mtd = db.session.query(
        func.count(func.distinct(WorkLog.ro_number))
    ).filter(
        WorkLog.date >= start_month,
        WorkLog.date <= metrics_date
    ).scalar() or 0

    raw_avg_hours_per_ro = (
        mtd_sold / total_ros_mtd
        if total_ros_mtd > 0 else 2
)

    closed_ros = RepairOrder.query.filter(
        RepairOrder.store_id == store_id,
        RepairOrder.status == "Closed"
    ).count()
        
    # simple approximation for now
    total_hours_today = (
        db.session.query(func.sum(WorkLog.flat_rate_hours))
        .join(TeamMember)
        .join(Team)
        .filter(
            Team.store_id == store_id,
            WorkLog.date == metrics_date
        )
        .scalar()
        or 0
    )

    route_summary = {
        "total_ros_mtd": total_ros_mtd,
        "active_ros": len(active_ros),
        "closed_ros": closed_ros,
        "total_hours": round(total_hours_today, 1)
    }

    # =====================================================
    # 4. PRODUCTION (MTD)
    # =====================================================
    


    expected_pace_hours = (
        monthly_frh_goal * (days_passed_work / total_work_days)
        if total_work_days > 0 else 0
    )

    

    mtd_deficit = expected_pace_hours - mtd_sold

    # --- FUTURE: DPO LOGIC ---
    techs = TeamMember.query.join(Team).filter(
        Team.store_id == store_id
    ).all()

    expected_hours_today = sum(
        tech.daily_production_objective or 0 for tech in techs
    )

    prod_pace = 0
    if expected_hours_today > 0:
        prod_pace = (total_hours_today / expected_hours_today) * 100

    tech_hours = {}

    for tech in techs:
        hours = (
            db.session.query(func.sum(WorkLog.flat_rate_hours))
            .filter(
                WorkLog.team_member_id == tech.id,
                WorkLog.date >= start_month,
                WorkLog.date <= metrics_date
            )
            .scalar()
            or 0
        )

        tech_hours[tech.id] = hours
    
    techs_below_dpo = 0
    techs_below_dpo_list = []
    
    
    target_buffer = 0.2  # allow some buffer below target DPO
    for tech in techs:
        if tech.name is None:
            continue  # skip if no name set

        if tech.daily_production_objective is None:
            continue  # skip if no DPO target set
    
        total_hours = tech_hours.get(tech.id, 0)

        if total_hours < 10:
            continue
        actual_dpo = total_hours / days_passed_work if days_passed_work > 0 else 0
        expected_dpo = tech.daily_production_objective

        if actual_dpo < (expected_dpo - target_buffer):
            techs_below_dpo += 1

            techs_below_dpo_list.append({
                "name": tech.name,
                "actual": round(actual_dpo, 1),
                "expected": round(expected_dpo, 1)
            })

    # =====================================================
    # 5. APPOINTMENTS
    # =====================================================

    # =====================================================
    # 6. DAILY METRICS (CLEAN + CORRECT ORDER)
    # =====================================================

    monthly_gross_goal = projected_gross

    today_metrics = DailyMetrics.query.filter_by(
        store_id=store_id,
        date=metrics_date
    ).first()

    # --- Inputs ---
    mtd_gross = today_metrics.mtd_gross if today_metrics else 0
    today_appts = today_metrics.today_appts if today_metrics else None
    appt_7_day = today_metrics.appt_7_day if today_metrics else None

    # =====================================================
    # 1. MTD EXPECTATIONS
    # =====================================================
    expected_mtd_gross = (
        monthly_gross_goal * days_passed_work / total_work_days
        if total_work_days > 0 else 0
    )

    gross_gap = expected_mtd_gross - mtd_gross

    # =====================================================
    # 2. BASE DAILY TARGET
    # =====================================================
    normal_daily_gross = (
        monthly_gross_goal / total_work_days
        if total_work_days > 0 else 0
    )

    # =====================================================
    # 3. TRUE TODAY NEED (INCLUDES RECOVERY)
    # =====================================================
    daily_recovery_gross = (
        gross_gap / remaining_work_days
        if remaining_work_days > 0 else 0
    )
    
    today_needed_gross = normal_daily_gross + daily_recovery_gross

    #if remaining_work_days > 0:
        #today_needed_gross += gross_gap / remaining_work_days

    # =====================================================
    # 4. CONVERT TO APPOINTMENTS (FIXED - USE PRODUCTION TARGET)
    # =====================================================
    
    unbooked_ro_hours = db.session.query(
        func.sum(WorkLog.flat_rate_hours)
    ).join(RepairOrder, WorkLog.ro_number == RepairOrder.ro_number).filter(
        RepairOrder.store_id == store_id,
        or_(RepairOrder.status == "Ready", RepairOrder.status == "Warranty"),
        WorkLog.date >= start_month,
        WorkLog.date <= metrics_date
    ).scalar() or 0

    adjusted_unbooked_hours = unbooked_ro_hours * 0.75
    daily_recovery = (mtd_deficit / remaining_work_days if remaining_work_days > 0 else 0)

    today_needed_hours = expected_hours_today + max(daily_recovery, 0) - adjusted_unbooked_hours# 🔥 THIS IS THE KEY
    today_needed_hours = max(today_needed_hours, 0)

    # avg hours per RO (MTD based)

    avg_hours_per_ro = max(1.5, min(raw_avg_hours_per_ro, 5.0))

    # final appointment target
    needed_appointments = int(
        (today_needed_hours / avg_hours_per_ro) * 1.15
    ) if avg_hours_per_ro > 0 else 0

    
    # =====================================================
    # 5. DELTAS (ONLY AFTER TARGET EXISTS)
    # =====================================================
    appointment_delta = None
    if today_appts is not None and needed_appointments > 0:
        appointment_delta = today_appts - needed_appointments

    appt_7_day_delta = None
    if appt_7_day is not None and needed_appointments > 0:
        appt_7_day_delta = appt_7_day - (needed_appointments * 7)

    
    # =====================================================
    # 6. CONTEXT METRIC
    # =====================================================
    gross_percent_of_normal = (
        today_needed_gross / normal_daily_gross
        if normal_daily_gross > 0 else 1
    )

    # =====================================================
    # 🔥 ACCOUNTABILITY ENGINE
    # =====================================================
    accountability_items = []

    if dispatch > inspection * 2 and dispatch > 10:
        accountability_items.append({
            "issue": "Dispatch Bottleneck",
            "key": "dispatch",
            "summary": f"{dispatch} dispatch / {inspection} inspection",
            "timeframe": "Now (1-2 hrs)"
        })

    if appointment_delta is not None and appointment_delta < 0:
        accountability_items.append({
            "issue": "Appointment Shortage",
            "key": "appointments",
            "summary": f"Short {abs(appointment_delta)}",
            "timeframe": "Today + 7 Days"
        })

    if mtd_deficit > 0:
        accountability_items.append({
            "issue": "Production Behind",
            "key": "production",
            "summary": f"{int(mtd_deficit)} FRH behind",
            "timeframe": "Daily"
        })

    # =====================================================
    # 🔥 RESPONSE HANDLING
    # =====================================================
    responses = {}

    if request.method == "POST":
        for item in accountability_items:
            key = item["key"]

            plan = request.form.get(f"{key}_plan", "")
            owner = request.form.get(f"{key}_owner", "")
            timing = request.form.get(f"{key}_timing", "")

            status, message = validate_response(key, plan)

            responses[key] = {
                "plan": plan,
                "owner": owner,
                "timing": timing,
                "status": status,
                "message": message
            }
    if today.weekday() == 6:  # Sunday
        today_needed_hours = 0
        needed_appointments = 0
        today_needed_gross = None
    is_sunday = today.weekday() == 6
    # =====================================================
    # 7. RENDER
    # =====================================================
    return render_template(
        "home.html",

        # core
        projected_gross=projected_gross,
        monthly_frh_goal=monthly_frh_goal,
        mtd_sold=mtd_sold,
        mtd_deficit=mtd_deficit,
        expected_pace_hours=expected_pace_hours,
        techs_below_dpo=techs_below_dpo,
        techs_below_dpo_list=techs_below_dpo_list,
        expected_hours_today=expected_hours_today,
        prod_pace=prod_pace,
        routesheet_audit=routesheet_audit,
        routesheet_audit_stale=routesheet_audit_stale,
        tech_hours_audit=tech_hours_audit,
        tech_hours_audit_stale=tech_hours_audit_stale,
        active_ros=active_ros,
        total_ros_mtd=total_ros_mtd,


        # workflow
        status_counts=status_counts,
        dispatch=dispatch,
        inspection=inspection,
        approval=approval,
        service=service,
        route_summary=route_summary,
        avg_hours_per_ro=avg_hours_per_ro,

        # appointments
        needed_appointments=needed_appointments,
        today_appts=today_appts,
        appointment_delta=appointment_delta,
        appt_7_day=appt_7_day,
        appt_7_day_delta=appt_7_day_delta,
        is_sunday=is_sunday,

        # gross
        mtd_gross=mtd_gross,
        expected_mtd_gross=expected_mtd_gross,
        today_needed_gross=today_needed_gross,
        normal_daily_gross=normal_daily_gross,
        gross_percent_of_normal=gross_percent_of_normal,

        # 🔥 NEW SYSTEM
        accountability_items=accountability_items,
        responses=responses
    )

# --- Daily input for performance tracking ---
@main_bp.route("/input-metrics", methods=["GET", "POST"])
@login_required
def input_metrics():

    if request.method == "POST":
        mtd_gross = float(request.form.get("mtd_gross") or 0)
        yesterday_gross = float(request.form.get("yesterday_gross") or 0)
        today_appts = int(request.form.get("today_appts") or 0)
        appt_7_day = int(request.form.get("appt_7_day") or 0)

        existing = DailyMetrics.query.filter_by(
            store_id=current_user.store_id,
            date=date.today() - timedelta(days=1)
        ).first()

        if existing:
            existing.mtd_gross = mtd_gross
            existing.yesterday_gross = yesterday_gross
            existing.today_appts = today_appts
            existing.appt_7_day = appt_7_day
        else:
            existing = DailyMetrics(
                store_id=current_user.store_id,
                date=date.today(),
                mtd_gross=mtd_gross,
                yesterday_gross=yesterday_gross,
                today_appts=today_appts,
                appt_7_day=appt_7_day

            )
            db.session.add(existing)

        db.session.commit()
        
        return redirect(url_for("main.home"))

    return render_template("input_metrics.html")


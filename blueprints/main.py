from operator import or_
from collections import defaultdict 
from flask import Blueprint, render_template, redirect, url_for, request, flash
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
from .schedule import count_workdays, get_holiday_dates

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

    user = current_user._get_current_object()

    if user.is_operator:
        return redirect(url_for("operator.store_index"))

    if not hasattr(user, "store_id"):
        return redirect(url_for("auth.login"))

    store_id = user.store_id

    # =====================================================
    # DATE LOGIC
    # =====================================================
    today = date.today()

    def get_last_workday(d):
        d = d - timedelta(days=1)
        while d.weekday() == 6:
            d -= timedelta(days=1)
        return d

    metrics_date = get_last_workday(today)
    is_sunday = today.weekday() == 6

    start_month = date(metrics_date.year, metrics_date.month, 1)
    next_month = (start_month.replace(day=28) + timedelta(days=4)).replace(day=1)
    end_of_month = next_month - timedelta(days=1)
    # =====================================================
    # WORKDAY CALCS
    # =====================================================
    # =====================================================
    # WORKDAY CALCS (REAL VERSION)
    # =====================================================

    holidays = set()

    for month in range(start_month.month, end_of_month.month + 1):
        holidays.update(get_holiday_dates(metrics_date.year, month, month))

    elapsed_work_days = count_workdays(start_month, metrics_date, holidays)
    total_work_days = count_workdays(start_month, end_of_month, holidays)
    remaining_work_days = max(total_work_days - elapsed_work_days, 1)

    # =====================================================
    # MTD HOURS (WORKLOG)
    # =====================================================
    mtd_sold = db.session.query(
        func.sum(WorkLog.flat_rate_hours)
    ).join(TeamMember).join(Team).filter(
        Team.store_id == store_id,
        WorkLog.date >= start_month,
        WorkLog.date <= metrics_date
    ).scalar() or 0

    # =====================================================
    # DAILY METRICS (MTD INPUT)
    # =====================================================
    today_metrics = DailyMetrics.query.filter_by(
        store_id=store_id,
        date=metrics_date
    ).first()

    mtd_total_gross = today_metrics.total_gross if today_metrics else 0

    today_appts = today_metrics.today_appts if today_metrics else 0
    appt_7_day = today_metrics.appt_7_day if today_metrics else 0

    # =====================================================
    # FORECAST
    # =====================================================
    forecast = FinancialForecast.query.filter_by(
        store_id=store_id,
        month=metrics_date.month,
        year=metrics_date.year
    ).first()

    projected_gross = forecast.total_gross if forecast else 0

    normal_daily_gross = (
        projected_gross / total_work_days
        if total_work_days > 0 else 0
    )

    # =====================================================
    # MTD GROSS
    # =====================================================
    mtd_labor_gross = db.session.query(
        func.sum(DailyMetrics.labor_gross)
    ).filter(
        DailyMetrics.store_id == store_id,
        DailyMetrics.date >= start_month,
        DailyMetrics.date <= metrics_date
    ).scalar() or 0

    mtd_total_gross = db.session.query(
        func.sum(DailyMetrics.total_gross)
    ).filter(
        DailyMetrics.store_id == store_id,
        DailyMetrics.date >= start_month,
        DailyMetrics.date <= metrics_date
    ).scalar() or 0


    # =====================================================
    # MTD POSITION
    # =====================================================
    expected_mtd_gross = (
        projected_gross * (elapsed_work_days / total_work_days)
        if total_work_days > 0 else 0
    )

    mtd_deficit = expected_mtd_gross - mtd_total_gross


    # =====================================================
    # GPH (REAL PERFORMANCE)
    # =====================================================
    DEFAULT_GPH = 120

    # --- ACTUAL GPH ---
    if mtd_sold > 0:
        actual_gph = mtd_labor_gross / mtd_sold
    else:
        actual_gph = None

    # --- FORECAST (FROM DB — NOT finance.py variable) ---
    forecast = FinancialForecast.query.filter_by(
        store_id=store_id,
        month=metrics_date.month,
        year=metrics_date.year
    ).first()

    forecast_gph = (
        forecast.labor_gross / forecast.expected_frh
        if forecast and forecast.expected_frh > 0
        else DEFAULT_GPH
    )

    # --- BLENDED GPH ---
    if actual_gph:
        gph = (actual_gph * 0.7) + (forecast_gph * 0.3)
    else:
        gph = forecast_gph

    # --- GUARDRAILS ---
    gph = max(min(gph, 200), 80)  
  
    # =====================================================
    # HOURS MODEL
    # =====================================================
    daily_base_hours = (
        normal_daily_gross / gph
        if gph > 0 else 0
    )

    mtd_deficit_hours = (
        mtd_deficit / gph
        if gph > 0 else 0
    )

    daily_recovery_hours = (
        mtd_deficit_hours / remaining_work_days
        if remaining_work_days > 0 else 0
    )

    # =====================================================
    # SMART RECOVERY (DYNAMIC CAP)
    # =====================================================

    severity = (
        abs(mtd_deficit) / projected_gross
        if projected_gross > 0 else 0
    )

    if severity < 0.05:
        cap_pct = 0.25
    elif severity < 0.10:
        cap_pct = 0.50
    else:
        cap_pct = 1.0   # no cap when things are bad

    recovery_cap = daily_base_hours * cap_pct

    daily_recovery_hours = max(
        min(daily_recovery_hours, recovery_cap),
        -recovery_cap
    )

    today_target_hours = daily_base_hours + daily_recovery_hours

    # =====================================================
    # MTD HOURS TRACKING
    # =====================================================
    mtd_target_hours = daily_base_hours * elapsed_work_days
    mtd_hours_gap = mtd_sold - mtd_target_hours

    # =====================================================
    # AVERAGE HOURS PER RO
    # =====================================================
    total_ros_mtd = db.session.query(
        func.count(func.distinct(WorkLog.ro_number))
    ).join(
        RepairOrder, WorkLog.ro_number == RepairOrder.ro_number
    ).filter(
        RepairOrder.store_id == store_id,
        WorkLog.date >= start_month,
        WorkLog.date <= metrics_date
    ).scalar() or 0

    raw_avg_hours = mtd_sold / total_ros_mtd if total_ros_mtd > 0 else 2
    avg_hours_per_ro = max(1.5, min(raw_avg_hours, 5.0))

    # =====================================================
    # APPOINTMENTS
    # =====================================================
    needed_appointments = int(
        today_target_hours / avg_hours_per_ro
    ) if avg_hours_per_ro > 0 else 0

    appointment_delta = today_appts - needed_appointments

    appt_7_day_delta = appt_7_day - (needed_appointments * 6)

    # =====================================================
    # WIP CAPACITY
    # =====================================================
    ros = RepairOrder.query.filter(
        RepairOrder.store_id == store_id,
        RepairOrder.status != "Closed"
    ).all()

    service_count = sum(1 for ro in ros if ro.status == "Service")
    dispatch_count = sum(1 for ro in ros if ro.status == "Dispatch")
    parts_count = sum(1 for ro in ros if ro.status == "Parts")
    ready_count = sum(1 for ro in ros if ro.status in ["Ready", "Warranty"])

    adjusted_wip_hours = (
        (service_count * 1.0) +
        (dispatch_count * 0.8) +
        (parts_count * 0.5) +
        (ready_count * 0.25)
    ) * (avg_hours_per_ro * 0.65)

    capacity_gap = adjusted_wip_hours - today_target_hours

    # =====================================================
    # SUNDAY OVERRIDE
    # =====================================================
    if is_sunday:
        needed_appointments = 0

    day_label = "Sunday - Monday Readiness" if is_sunday else "Today"

    # =====================================================
    # DEBUG
    # =====================================================
    print("---- CLEAN MODEL DEBUG ----")
    print("MTD Actual:", mtd_total_gross)
    print("MTD Target:", expected_mtd_gross)
    print("MTD Deficit:", mtd_deficit)
    print("GPH:", gph)
    print("Today Target Hours:", today_target_hours)
    print("Capacity Gap:", capacity_gap)
    print("Needed Appts:", needed_appointments)
    print("--------------------------")
    print("---- WORKDAY DEBUG ----")
    print("Start of Month:", start_month)
    print("Metrics Date:", metrics_date)
    print("End of Month:", end_of_month)

    print("Total Work Days:", total_work_days)
    print("Elapsed Work Days:", elapsed_work_days)
    print("Remaining Work Days:", remaining_work_days)

    if total_work_days > 0:
        print("Daily Target Gross:", projected_gross / total_work_days)
    print("Total Work Days:", total_work_days)
    print("Elapsed Work Days:", elapsed_work_days)
    print("------------------------")

    # =====================================================
    # RENDER
    # =====================================================
    return render_template(
        "home.html",
        mtd_total_gross=mtd_total_gross,
        expected_mtd_gross=expected_mtd_gross,
        mtd_deficit=mtd_deficit,
        mtd_target_hours=mtd_target_hours,
        mtd_sold=mtd_sold,
        mtd_hours_gap=mtd_hours_gap,
        today_target_hours=today_target_hours,
        needed_appointments=needed_appointments,
        today_appts=today_appts,
        appointment_delta=appointment_delta,
        appt_7_day=appt_7_day,
        appt_7_day_delta=appt_7_day_delta,
        capacity_gap=capacity_gap,
        adjusted_wip_hours=adjusted_wip_hours,
        avg_hours_per_ro=avg_hours_per_ro,
        normal_daily_gross=normal_daily_gross,
        gph=gph,
        is_sunday=is_sunday,
        day_label=day_label
    )

        # --- Daily input for performance tracking ---
@main_bp.route("/input-metrics", methods=["GET", "POST"])
@login_required
def input_metrics():

    def get_last_workday(d):
        d = d - timedelta(days=1)
        while d.weekday() == 6:
            d -= timedelta(days=1)
        return d

    metrics_date = get_last_workday(date.today())

    if request.method == "POST":
        labor_gross = float(request.form.get("labor_gross") or 0)
        parts_gross = float(request.form.get("parts_gross") or 0)
        sublet_gross = float(request.form.get("sublet_gross") or 0)

        total_gross = labor_gross + parts_gross + sublet_gross

        today_appts = int(request.form.get("today_appts") or 0)
        appt_7_day = int(request.form.get("appt_7_day") or 0)

        metrics = DailyMetrics.query.filter_by(
            store_id=current_user.store_id,
            date=metrics_date
        ).first()

        if not metrics:
            metrics = DailyMetrics(
                store_id=current_user.store_id,
                date=metrics_date
            )
            db.session.add(metrics)

        metrics.labor_gross = labor_gross
        metrics.parts_gross = parts_gross
        metrics.sublet_gross = sublet_gross
        metrics.total_gross = total_gross
        metrics.today_appts = today_appts
        metrics.appt_7_day = appt_7_day

        db.session.commit()

        print("✅ Saved DailyMetrics")
        print("Date:", metrics_date)
        print("Store:", current_user.store_id)
        print("Labor:", labor_gross)
        print("Parts:", parts_gross)
        print("Sublet:", sublet_gross)
        print("Total:", total_gross)

        flash("Daily metrics saved successfully", "success")
        return redirect(url_for("main.home"))

    metrics = DailyMetrics.query.filter_by(
        store_id=current_user.store_id,
        date=metrics_date
    ).first()

    return render_template(
        "input_metrics.html",
        metrics=metrics,
        metrics_date=metrics_date
    )

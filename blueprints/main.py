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

    # =====================================================
    # WORKDAY CALCS
    # =====================================================
    def count_workdays(start_date, end_date):
        day_count = 0
        current = start_date
        while current <= end_date:
            if current.weekday() != 6:
                day_count += 1
            current += timedelta(days=1)
        return day_count

    days_passed_work = count_workdays(start_month, metrics_date)

    next_month = (start_month.replace(day=28) + timedelta(days=4)).replace(day=1)
    end_of_month = next_month - timedelta(days=1)

    total_work_days = count_workdays(start_month, end_of_month)
    remaining_work_days = max(total_work_days - days_passed_work, 1)

    # =====================================================
    # WORKLOG (MTD HOURS)
    # =====================================================
    mtd_logs = WorkLog.query.join(TeamMember).join(Team).filter(
        Team.store_id == store_id,
        WorkLog.date >= start_month,
        WorkLog.date <= metrics_date
    ).all()

    mtd_sold = 0

    for log in mtd_logs:
        if log.team_member_id and log.flat_rate_hours:
            mtd_sold += float(log.flat_rate_hours)

    total_ros_mtd = db.session.query(
        func.count(func.distinct(WorkLog.ro_number))
    ).join(
        RepairOrder, WorkLog.ro_number == RepairOrder.ro_number
    ).filter(
        RepairOrder.store_id == store_id,
        WorkLog.date >= start_month,
        WorkLog.date <= metrics_date
    ).scalar() or 0

    raw_avg_hours_per_ro = mtd_sold / total_ros_mtd if total_ros_mtd > 0 else 2
    avg_hours_per_ro = max(1.5, min(raw_avg_hours_per_ro, 5.0))

    # =====================================================
    # DAILY METRICS
    # =====================================================
    today_metrics = DailyMetrics.query.filter_by(
        store_id=store_id,
        date=metrics_date
    ).first()

    # =====================================================
    # MTD LABOR GROSS (NEW CLEAN VERSION)
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

    today_appts = today_metrics.today_appts if today_metrics else None
    appt_7_day = today_metrics.appt_7_day if today_metrics else None

    # =====================================================
    # GROSS TARGET LOGIC
    # =====================================================
    projected_gross = 500000  # TODO: replace

    expected_mtd_gross = (
        projected_gross * days_passed_work / total_work_days
        if total_work_days > 0 else 0
    )

    mtd_deficit = expected_mtd_gross - mtd_total_gross

    normal_daily_gross = (
        projected_gross / total_work_days
        if total_work_days > 0 else 0
    )

    # =====================================================
    # HOURS LOGIC (FIXED)
    # =====================================================
    gross_per_hour = (
        mtd_labor_gross / mtd_sold
        if mtd_sold > 0 else 120
    )
    expected_hours_today = normal_daily_gross / gross_per_hour

    mtd_deficit_hours = mtd_deficit / gross_per_hour

    recovery = 0
    if mtd_deficit_hours > 0 and remaining_work_days > 0:
        max_push = expected_hours_today * 0.5
        recovery = min(mtd_deficit_hours / remaining_work_days, max_push)

    today_needed_hours = expected_hours_today + recovery

    # =====================================================
    # UNBOOKED ADJUSTMENT
    # =====================================================
    unbooked_ro_hours = db.session.query(
        func.sum(WorkLog.flat_rate_hours)
    ).join(
        RepairOrder, WorkLog.ro_number == RepairOrder.ro_number
    ).filter(
        RepairOrder.store_id == store_id,
        or_(
            RepairOrder.status == "Ready",
            RepairOrder.status == "Warranty"
        ),
        WorkLog.date >= start_month,
        WorkLog.date <= metrics_date
    ).scalar() or 0

    adjusted_unbooked_hours = unbooked_ro_hours * 0.75

    today_needed_hours -= adjusted_unbooked_hours
    today_needed_hours = max(today_needed_hours, 0)

    # =====================================================
    # ROUTE SHEET (WIP)
    # =====================================================
    ros = RepairOrder.query.filter(
        RepairOrder.store_id == store_id,
        RepairOrder.status != "Closed"
    ).all()

    service_count = sum(1 for ro in ros if ro.status == "Service")
    dispatch_count = sum(1 for ro in ros if ro.status == "Dispatch")
    parts_count = sum(1 for ro in ros if ro.status == "Parts")
    ready_count = sum(1 for ro in ros if ro.status in ["Ready", "Warranty"])

    # =====================================================
    # WIP CAPACITY
    # =====================================================
    adjusted_wip_hours = (
        (service_count * 1.0) +
        (dispatch_count * 0.8) +
        (parts_count * 0.5) +
        (ready_count * 0.25)
    ) * (avg_hours_per_ro * 0.65)

    capacity_gap = adjusted_wip_hours - today_needed_hours

    # =====================================================
    # SUNDAY OVERRIDE (LAST)
    # =====================================================
    if is_sunday:
            today_needed_hours = 0
            needed_appointments = 0
            # DO NOT zero capacity_gap - we want to see gap for monday prep even if it's sunday
            # evaluate capacity against a NORMAL day
            capacity_gap = adjusted_wip_hours - expected_hours_today

    # =====================================================
    # APPOINTMENTS
    # =====================================================
    needed_appointments = int(
        (today_needed_hours / avg_hours_per_ro) * 1.15
    ) if avg_hours_per_ro > 0 else 0

    appointment_delta = None
    if today_appts is not None and needed_appointments > 0:
        appointment_delta = today_appts - needed_appointments

    appt_7_day_delta = None
    if appt_7_day is not None:
        appt_7_day_delta = appt_7_day - (needed_appointments * 6)

    day_label = "Sunday - Monday Readiness" if is_sunday else "Today"
    display_needed_hours = expected_hours_today if is_sunday else today_needed_hours

    # =====================================================
    # DEBUG
    # =====================================================
    print("---- CAPACITY DEBUG ----")
    print("Adjusted WIP Hours:", adjusted_wip_hours)
    print("Today Needed Hours:", today_needed_hours)
    print("Capacity Gap:", capacity_gap)
    print("Today:", today)
    print("Metrics Date:", metrics_date)
    print("Is Sunday:", is_sunday)
    print("normal_daily_gross:", normal_daily_gross)
    print("gross_per_hour:", gross_per_hour)
    print("expected_hours_today:", expected_hours_today)
    print("mtd_labor_gross:", mtd_labor_gross)
    print("mtd_sold:", mtd_sold)
    print("gross_per_hour:", gross_per_hour)
    print("mtd_total_gross:", mtd_total_gross)
    print("------------------------")
    logs = WorkLog.query.all()
    print("TOTAL LOGS:", len(logs))

    for log in logs[:5]:
        print(log.date, log.flat_rate_hours, log.id)
    # =====================================================
    # RENDER
    # =====================================================
    return render_template(
        "home.html",
        mtd_total_gross=mtd_total_gross,
        expected_mtd_gross=expected_mtd_gross,
        today_needed_hours=today_needed_hours,
        expected_hours_today=expected_hours_today,
        capacity_gap=capacity_gap,
        needed_appointments=needed_appointments,
        today_appts=today_appts,
        appointment_delta=appointment_delta,
        appt_7_day=appt_7_day,
        appt_7_day_delta=appt_7_day_delta,
        avg_hours_per_ro=avg_hours_per_ro,
        is_sunday=is_sunday,
        mtd_deficit=mtd_deficit,
        day_label=day_label,
        adjusted_wip_hours=adjusted_wip_hours,
        display_needed_hours=display_needed_hours
    )

# --- Daily input for performance tracking ---
@main_bp.route("/input-metrics", methods=["GET", "POST"])
@login_required
def input_metrics():

    if request.method == "POST":

        labor_gross = float(request.form.get("labor_gross", 0) or 0)
        parts_gross = float(request.form.get("parts_gross", 0) or 0)
        sublet_gross = float(request.form.get("sublet_gross", 0) or 0)

        # 🧠 auto-calc total (no human math mistakes)
        total_gross = labor_gross + parts_gross + sublet_gross

        today_appts = int(request.form.get("today_appts", 0) or 0)
        appt_7_day = int(request.form.get("appt_7_day", 0) or 0)

        # use same logic as home route
        metrics_date = date.today() - timedelta(days=1)

        existing = DailyMetrics.query.filter_by(
            store_id=current_user.store_id,
            date=metrics_date
        ).first()

        if existing:
            existing.total_gross = total_gross
            existing.labor_gross = labor_gross
            existing.parts_gross = parts_gross
            existing.sublet_gross = sublet_gross
            existing.today_appts = today_appts
            existing.appt_7_day = appt_7_day
        else:
            existing = DailyMetrics(
                store_id=current_user.store_id,
                date=metrics_date,
                total_gross=total_gross,
                labor_gross=labor_gross,
                parts_gross=parts_gross,
                sublet_gross=sublet_gross,
                today_appts=today_appts,
                appt_7_day=appt_7_day
            )
            db.session.add(existing)

        db.session.commit()

        print("Saved Metrics:")
        print("Labor:", labor_gross)
        print("Parts:", parts_gross)
        print("Sublet:", sublet_gross)
        print("Total:", total_gross)

        return redirect(url_for("main.home"))

    return render_template("input_metrics.html")


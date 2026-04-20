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


# =========================================================
# ROUTES
# =========================================================
@main_bp.route("/help")
@login_required
def help_page():
    return render_template("help.html", title="User Manual")


@main_bp.route("/")
@main_bp.route("/home")
@login_required
def home():
    user = current_user._get_current_object()

    if user.is_operator:
        return redirect(url_for("operator.store_index"))

    if not hasattr(user, "store_id"):
        return redirect(url_for("auth.login"))

    store_id = user.store_id
    today = date.today()
    now = datetime.now()
    pacific = pytz.timezone("US/Pacific")
    pacific_now = datetime.now(pacific)

    # =====================================================
    # 1. FORECAST / STATIC INPUTS
    # =====================================================
    forecast = FinancialForecast.query.filter_by(
        store_id=store_id, month=today.month, year=today.year
    ).first()

    projected_gross = forecast.total_gross if forecast else 0.0
    monthly_frh_goal = forecast.expected_frh if forecast else 0.0

    fin_inputs = FinancialInputs.query.filter_by(user_id=current_user.id).first()

    # =====================================================
    # 2. CALENDAR / WORKDAY CONTEXT
    # =====================================================
    _, days_in_month = calendar.monthrange(today.year, today.month)
    is_working_day = today.weekday() < 6  # Mon-Sat

    total_work_days = 0
    days_passed_work = 0

    for d in range(1, days_in_month + 1):
        current_d = date(today.year, today.month, d)
        if current_d.weekday() < 6:
            total_work_days += 1
            if d <= today.day:
                days_passed_work += 1

    work_progress_pct = (days_passed_work / total_work_days) if total_work_days > 0 else 0
    expected_pace_hours = monthly_frh_goal * work_progress_pct

    start_month = date(today.year, today.month, 1)
    remaining_work_days = total_work_days - days_passed_work

    # =====================================================
    # 3. WORKFLOW PULSE
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

    dispatch = status_counts.get("Dispatch", 0)
    inspection = status_counts.get("Inspection", 0)
    approval = status_counts.get("Approval", 0)
    service = status_counts.get("Service", 0)

    late_ros = []
    warning_ros = []

    for ro in active_ros:
        if ro.status in status_counts:
            status_counts[ro.status] += 1
        elif ro.status == "Warranty / Wash":
            status_counts["Warranty"] += 1

        if ro.promised_time:
            if ro.promised_time < now:
                late_ros.append(ro)
            elif ro.promised_time <= now + timedelta(hours=2):
                warning_ros.append(ro)

    late_ros.sort(key=lambda x: x.promised_time)
    warning_ros.sort(key=lambda x: x.promised_time)

    # =====================================================
    # 4. PRODUCTION (TODAY)
    # =====================================================
    today_production = (
        db.session.query(func.sum(WorkLog.flat_rate_hours))
        .join(TeamMember)
        .join(Team)
        .filter(
            Team.store_id == store_id,
            WorkLog.date == today,
        )
        .scalar()
        or 0.0
    )

    all_techs = TeamMember.query.join(Team).filter(Team.store_id == store_id).all()
    daily_goal = 0.0
    absent_techs = []

    for tech in all_techs:
        entry = ScheduleEntry.query.filter_by(team_member_id=tech.id, date=today).first()
        if entry:
            if entry.schedule_type == "WORK":
                if (
                    hasattr(tech, "dpo_calculation_mode")
                    and tech.dpo_calculation_mode == "calculated"
                ):
                    daily_goal += tech.calculated_dpo or 0.0
                else:
                    daily_goal += tech.daily_production_objective or 0.0
            else:
                absent_techs.append({"name": tech.name, "reason": entry.schedule_type})

    prod_pace = (today_production / daily_goal * 100) if daily_goal > 0 else 0.0
    needed_today_hours = daily_goal
    remaining_today_hours = max(daily_goal - today_production, 0)

    # =====================================================
    # 5. MTD BASELINE / EFFICIENCY
    # =====================================================
    efficiency_stats = (
        db.session.query(
            func.sum(WorkLog.flat_rate_hours),
            func.sum(WorkLog.actual_time),
            func.count(func.distinct(WorkLog.ro_number)),
        )
        .join(TeamMember)
        .join(Team)
        .filter(
            Team.store_id == store_id,
            WorkLog.date >= start_month,
            WorkLog.date <= today,
        )
        .first()
    )

    mtd_sold = efficiency_stats[0] or 0.0
    mtd_actual = efficiency_stats[1] or 0.0
    mtd_ro_count = efficiency_stats[2] or 0

    shop_efficiency = (mtd_sold / mtd_actual * 100) if mtd_actual > 0 else 0.0
    hours_per_ro = (mtd_sold / mtd_ro_count) if mtd_ro_count > 0 else 0.0

    mtd_deficit = expected_pace_hours - mtd_sold
    severity_ratio = mtd_deficit / monthly_frh_goal

    if mtd_deficit >= 200:
        deficit_level = "Significantly Behind"
    elif mtd_deficit >= 100:
        deficit_level = "Moderately Behind"
    elif mtd_deficit > 0:
        deficit_level = "Slightly Behind"
    else:
        deficit_level = "On Track"

    if mtd_deficit > 0:
        mtd_status = "🔴 Off Pace"
    else:
        mtd_status = "🟢 On Pace"

    if mtd_deficit > 0:
        mtd_status_detail = f"{deficit_level} by {int(mtd_deficit)} hrs"
    else:
        mtd_status_detail = f"Ahead of MTD Pace by {abs(int(mtd_deficit))} hrs"

    # =====================================================
    # 6. TODAY GROSS TARGET
    # =====================================================
    today_labor_gross = 0.0
    today_parts_gross = 0.0
    today_total_gross = 0.0

    if fin_inputs and daily_goal > 0:
        elr = fin_inputs.effective_labor_rate or 0
        parts_ratio = fin_inputs.parts_to_labor_ratio or 0
        labor_margin = (fin_inputs.labor_margin or 0) / 100
        parts_margin = (fin_inputs.parts_margin or 0) / 100

        labor_revenue = daily_goal * elr
        parts_revenue = labor_revenue * parts_ratio

        today_labor_gross = labor_revenue * labor_margin
        today_parts_gross = parts_revenue * parts_margin
        today_total_gross = today_labor_gross + today_parts_gross

    # =====================================================
    # 7. APPOINTMENTS / NEED
    # =====================================================
    needed_appointments = 0
    if hours_per_ro > 0 and daily_goal > 0:
        needed_appointments = round(daily_goal / hours_per_ro)

    cp_needed = round(needed_appointments * 0.70)
    wp_needed = needed_appointments - cp_needed


    # --- Daily Metrics ---

    monthly_gross_goal = projected_gross  # your capacity target
    today_metrics = DailyMetrics.query.filter_by(
        store_id=store_id,
        date=date.today()
    ).first()

    metrics_entered_today = today_metrics is not None


    mtd_gross = today_metrics.mtd_gross if today_metrics else 0
    yesterday_gross = today_metrics.yesterday_gross if today_metrics else 0
    today_appts = today_metrics.today_appts if today_metrics else 0
    if needed_appointments > 0:
        appointment_delta = today_appts - needed_appointments
    else:
        appointment_delta = 0
    expected_mtd_gross = (monthly_gross_goal * days_passed_work / total_work_days if total_work_days > 0 else 0)

    

    gross_gap = expected_mtd_gross - mtd_gross

    today_needed_gross = 0
    normal_daily_gross = monthly_gross_goal / total_work_days if total_work_days > 0 else 0

    if remaining_work_days > 0:
        recovery_piece = gross_gap / remaining_work_days
        today_needed_gross = normal_daily_gross + recovery_piece

    today_needed_gross = max(today_needed_gross, 0)

    
    # =====================================================
    # 8. UTILIZATION / CAPACITY
    # =====================================================
    total_bays = 0
    monthly_planned_utilization = 0.0
    mtd_utilization = 0.0
    projected_eod = 0.0

    if fin_inputs:
        total_bays = (fin_inputs.bays_with_lifts or 0) + (fin_inputs.bays_without_lifts or 0)

    if total_bays > 0 and total_work_days > 0:
        shop_monthly_capacity = total_bays * 8 * total_work_days
        if shop_monthly_capacity > 0:
            monthly_planned_utilization = (monthly_frh_goal / shop_monthly_capacity) * 100

    if total_bays > 0 and days_passed_work > 0:
        mtd_capacity = total_bays * 8 * days_passed_work
        if mtd_capacity > 0:
            mtd_utilization = (mtd_sold / mtd_capacity) * 100

    mtd_utilization = round(mtd_utilization, 1)

    bay_daily_capacity = total_bays * 8 if total_bays > 0 else 0

    elapsed_hours = get_elapsed_work_hours()
    total_work_hours = 10

    if elapsed_hours > 0:
        projected_eod = (today_production / elapsed_hours) * total_work_hours
    projected_eod = max(projected_eod, 0)

    forecasted_hours_today = daily_goal
    current_hours_today = today_production

    forecasted_utilization = 0.0
    if bay_daily_capacity > 0:
        forecasted_utilization = (forecasted_hours_today / bay_daily_capacity) * 100
    forecasted_utilization = min(round(forecasted_utilization, 1), 150)

    current_utilization = 0.0
    if bay_daily_capacity > 0:
        current_utilization = (current_hours_today / bay_daily_capacity) * 100
    current_utilization = min(round(current_utilization, 1), 150)

    capacity_gap_hours = round(max(forecasted_hours_today - current_hours_today, 0), 1)

    capacity_gap_pct = 0.0
    if forecasted_hours_today > 0:
        capacity_gap_pct = round((capacity_gap_hours / forecasted_hours_today) * 100, 1)

    utilization_vs_plan = round(forecasted_utilization - monthly_planned_utilization, 1)

    # =====================================================
    # 9. TREND DIRECTION
    # =====================================================
    recent_days = []
    prior_days = []

    d = today
    while len(recent_days) + len(prior_days) < 6:
        if d.weekday() < 6:
            day_hours = (
                db.session.query(func.sum(WorkLog.flat_rate_hours))
                .join(TeamMember)
                .join(Team)
                .filter(
                    Team.store_id == store_id,
                    WorkLog.date == d,
                )
                .scalar()
                or 0.0
            )

            if len(recent_days) < 3:
                recent_days.append(day_hours)
            else:
                prior_days.append(day_hours)

        d -= timedelta(days=1)

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

    # =====================================================
    # 10. RECOVERY MODEL
    # =====================================================
    remaining_hours_needed = max(monthly_frh_goal - mtd_sold, 0)

    required_daily_recovery = 0.0
    recovery_status = "🟢 Achievable"

    if remaining_work_days > 0:
        required_daily_recovery = remaining_hours_needed / remaining_work_days

    if daily_goal > 0:
        if required_daily_recovery > daily_goal * 1.2:
            recovery_status = "🔴 Unrealistic Recovery"
        elif required_daily_recovery > daily_goal:
            recovery_status = "🟡 Aggressive Recovery"
        else:
            recovery_status = "🟢 Achievable"
    elif remaining_hours_needed > 0:
        recovery_status = "🔴 No Remaining Daily Capacity Signal"

    required_daily_recovery = round(required_daily_recovery, 1)
    remaining_hours_needed = round(remaining_hours_needed, 1)

    recovery_ros_per_day = 0
    if hours_per_ro > 0:
        recovery_ros_per_day = round(required_daily_recovery / hours_per_ro)

    # =====================================================
    # 11. PROJECTED MONTH-END OUTCOME
    # =====================================================
    projected_month_end = 0.0
    projection_delta = 0.0
    projection_status = "🟢 On Track to Hit Target"

    if days_passed_work > 0:
        avg_daily_output = mtd_sold / days_passed_work
        projected_month_end = avg_daily_output * total_work_days

    projection_delta = projected_month_end - monthly_frh_goal

    if projection_delta < -0.1 * monthly_frh_goal:
        projection_status = "🔴 Will Miss Target"
    elif projection_delta < 0:
        projection_status = "🟡 Slightly Under Target"
    else:
        projection_status = "🟢 On Track to Hit Target"

    projected_month_end = round(projected_month_end, 1)
    projection_delta = round(projection_delta, 1)

    # =====================================================
    # 12. PROJECTION CONFIDENCE
    # =====================================================
    confidence_level = "🟡 Moderate Confidence"
    confidence_score = 1.0

    gap_ratio = 0.0
    if monthly_frh_goal > 0:
        gap_ratio = abs(projection_delta) / monthly_frh_goal

    recovery_pressure = 0.0
    if daily_goal > 0:
        recovery_pressure = required_daily_recovery / daily_goal

    if gap_ratio > 0.2:
        confidence_score -= 0.4
    elif gap_ratio > 0.1:
        confidence_score -= 0.2

    if recovery_pressure > 1.2:
        confidence_score -= 0.4
    elif recovery_pressure > 1.0:
        confidence_score -= 0.2

    confidence_score = max(min(confidence_score, 1.0), 0.0)

    if confidence_score >= 0.75:
        confidence_level = "🟢 High Confidence"
    elif confidence_score >= 0.5:
        confidence_level = "🟡 Moderate Confidence"
    else:
        confidence_level = "🔴 Low Confidence"

    # =====================================================
    # 13. EARLY WARNING SYSTEM
    # =====================================================
    early_warning_triggered = False
    early_warning_level = "🟢 Stable"
    early_warning_message = "No immediate risk detected"

    is_projection_bad = projection_delta < 0
    is_low_confidence = confidence_score < 0.5
    is_declining = trend == "Declining"
    days_remaining = remaining_work_days

    if is_projection_bad and is_low_confidence and is_declining:
        early_warning_triggered = True
        early_warning_level = "🔴 Critical"
        early_warning_message = "Performance declining with low recovery probability"
    elif is_projection_bad and is_low_confidence:
        early_warning_triggered = True
        early_warning_level = "🟠 High Risk"
        early_warning_message = "Unlikely to hit target without immediate improvement"
    elif is_projection_bad and trend != "Improving":
        early_warning_triggered = True
        early_warning_level = "🟡 Warning"
        early_warning_message = "Behind plan and not improving"

    if early_warning_triggered and days_remaining <= 5:
        early_warning_level = "🔴 Critical"
        early_warning_message += " (Very limited time remaining)"
    elif early_warning_triggered and days_remaining <= 10:
        if early_warning_level != "🔴 Critical":
            early_warning_level = "🟠 High Risk"
        early_warning_message += " (Time window closing)"

    # =====================================================
    # 14. IMPROVEMENT SIGNAL FOR ADAPTIVE HISTORY
    # =====================================================
    improved = False
    if trend == "Improving":
        improved = True
    elif monthly_frh_goal > 0 and mtd_deficit < 0.05 * monthly_frh_goal:
        improved = True

    
    if days_passed_work > 0 and mtd_gross > 0:
        true_forecast_gross = (mtd_gross / days_passed_work) * total_work_days
    else:
        true_forecast_gross = projected_gross * 0.8  # fallback assumption
        
    forecast_gap = monthly_gross_goal - true_forecast_gross
    # =====================================================
    # 15. RECOMMENDED ACTIONS ENGINE (AUTO-PRIORITIZED)
    # =====================================================

    # --- CONTEXT ---
    current_context = {
        "dispatch": dispatch,
        "inspection": inspection,
        "approval": approval,
        "service": service
    }

    # --- REASON ENGINE (MOVE HERE - NOT BELOW) ---
    def generate_reasons(context: dict, forecast_gap: float, monthly_gross_goal: float) -> list:
        dispatch = context.get("dispatch", 0) or 0
        inspection = context.get("inspection", 0) or 0
        approval = context.get("approval", 0) or 0
        service = context.get("service", 0) or 0

        reasons = []

        if monthly_gross_goal > 0 and forecast_gap > 0:
            reasons.append((
                forecast_gap / monthly_gross_goal,
                "Current pace will miss gross target"
            ))

        def safe_ratio(a, b):
            return a / b if b > 0 else 0

        approval_vs_dispatch = safe_ratio(approval, dispatch)
        inspection_vs_dispatch = safe_ratio(inspection, dispatch)
        service_vs_approval = safe_ratio(service, approval)

        if approval_vs_dispatch > 1.2:
            reasons.append((approval_vs_dispatch * 1.2, "Approval backlog is blocking revenue"))

        if inspection_vs_dispatch < 0.7 and (dispatch - inspection) > 5:
            reasons.append((1 - inspection_vs_dispatch, "Inspection throughput is lagging behind incoming work"))

        if service < dispatch * 0.7:
            reasons.append((min(dispatch - service, 10), "Insufficient work reaching technicians"))

        if service_vs_approval > 1.2:
            reasons.append((service_vs_approval, "Service capacity is outpacing approvals"))

        if not reasons:
            reasons.append((0.5, "Workflow imbalance detected across stages"))

        reasons.sort(key=lambda x: (round(x[0], 2), random.random()), reverse=True)
        return [r[1] for r in reasons[:2]]


    # --- WEIGHTS ---
    weights = DecisionWeights.query.filter_by(store_id=store_id).first()

    if not weights:
        weights = DecisionWeights(
            store_id=store_id,
            base_weight=1.0,
            history_weight=2.0,
            context_weight=1.5,
        )
        db.session.add(weights)
        db.session.commit()

    BASE_WEIGHT = weights.base_weight
    HISTORY_WEIGHT = weights.history_weight
    CONTEXT_WEIGHT = weights.context_weight

    scored_actions = []


    def add_action(text, impact=1, urgency=1, bottleneck=1):
        base_score = (impact * 2) + (urgency * 2) + (bottleneck * 3)

        # --- HISTORY ---
        success_rate = get_action_history_success_rate(store_id, text)
        history_score = get_history_score(success_rate)

        # --- CONTEXT ---
        context_score = get_context_match_score(text, current_context, store_id)

        # --- FINAL SCORE ---
        score = (
            (base_score * BASE_WEIGHT)
            + (history_score * HISTORY_WEIGHT)
            + (context_score * CONTEXT_WEIGHT * 5)
        )

        # --- CONFIDENCE ---
        data_points = ActionHistory.query.filter_by(
            store_id=store_id,
            action_text=text
        ).count()

        volume_score = min(data_points / 10, 1)
        consistency_score = success_rate if success_rate is not None else 0
        context_strength = context_score

        confidence_score = (
            (volume_score * 0.4)
            + (consistency_score * 0.4)
            + (context_strength * 0.2)
        )

        if confidence_score >= 0.75:
            confidence_label = "🟢 High"
        elif confidence_score >= 0.5:
            confidence_label = "🟡 Medium"
        else:
            confidence_label = "🔴 Low"

        # --- REASONS ---
        reasons = generate_reasons(current_context, forecast_gap, monthly_gross_goal)

        # --- FINAL OUTPUT ---
        scored_actions.append({
            "text": text,
            "priority_score": round(score, 2),
            "priority": get_priority_label(score),
            "why": reasons,

            # keep for backend logic
            "confidence": confidence_label,
            "confidence_score": round(confidence_score, 2),

            "debug": {
                "base": round(base_score, 2),
                "history": round(history_score, 2),
                "context": round(context_score, 2),
                "success_rate": round(success_rate * 100, 1) if success_rate is not None else None,
                "data_points": data_points
            }
        })


    # --- ACTION GENERATION LOGIC (UNCHANGED) ---
    if early_warning_level == "🔴 Critical":
        if service == 0 and dispatch > 0:
            add_action("Assign work to technicians immediately", 3, 3, 3)
            add_action("Move highest value ROs into service", 3, 3, 3)
            add_action("Verify all techs are actively working", 2, 3, 2)
        elif approval > service:
            add_action("Call all pending approvals immediately", 3, 3, 3)
            add_action("Prioritize high-dollar ROs", 2, 3, 2)
            add_action("Clear approval backlog within 1 hour", 2, 3, 3)
        elif inspection > service * 2:
            add_action("Push inspections to completion", 3, 3, 3)
            add_action("Move completed inspections to approval", 2, 2, 3)
            add_action("Assign additional diagnostic support", 2, 2, 2)
        else:
            add_action("Increase car count immediately", 3, 3, 2)
            add_action("Prioritize quick-turn jobs", 2, 3, 2)
            add_action("Reduce technician idle time aggressively", 2, 3, 2)

    elif early_warning_level == "🟠 High Risk":
        if dispatch > service:
            add_action("Increase dispatch rate", 2, 2, 3)
            add_action("Ensure bays stay fully loaded", 2, 2, 2)
            add_action("Balance work across technicians", 2, 2, 2)
        elif approval > 0:
            add_action("Focus on approvals to unlock work", 2, 2, 3)
            add_action("Call customers with pending decisions", 2, 2, 2)
            add_action("Prioritize large jobs", 2, 2, 2)
        else:
            add_action("Improve workflow efficiency; Review dispatch process", 1, 2, 1)
            add_action("Reduce downtime between jobs; Inspect repair processes", 1, 2, 1)
            add_action("Focus on consistent throughput; Hold process is suspect", 1, 2, 1)

    elif early_warning_level == "🟡 Warning":
        add_action("Monitor pacing closely", 1, 2, 1)
        add_action("Address minor workflow delays", 1, 2, 1)
        add_action("Maintain steady production flow", 1, 1, 1)

    else:
        add_action("Maintain current performance", 1, 1, 1)
        add_action("Watch for emerging bottlenecks", 1, 1, 1)
        add_action("Keep workflow balanced", 1, 1, 1)

    if daily_goal > 0:
        if required_daily_recovery > daily_goal * 1.2:
            add_action("Increase capacity by dispatching work to idle technicians", 3, 3, 2)
        elif required_daily_recovery > daily_goal:
            add_action("Increase output beyond normal capacity", 2, 2, 2)


    # --- SORT + SELECT ---
    scored_actions.sort(key=lambda x: x["priority_score"], reverse=True)
    recommended_actions = scored_actions[:5]
    
    low_conf_count = 0

    for a in recommended_actions:
        if a.get("confidence") == "🔴 Low":
            low_conf_count += 1

    total_actions = len(recommended_actions)
    low_conf_ratio = (low_conf_count / total_actions) if total_actions > 0 else 0

    low_confidence_alert = False
    low_confidence_message = ""

    if low_conf_ratio >= 0.6:
        if early_warning_level in ["🔴 Critical", "🟠 High Risk"]:
            low_confidence_alert = True
            low_confidence_message = "Short data period may limit recommendation confidence during critical performance periods"
        else:
            low_confidence_alert = True
            low_confidence_message = "System lacks sufficient data for confident recommendations"
    # =====================================================
    # 16. Reason Generator
    # =====================================================
    
    # =====================================================
    # 17. SAVE ACTION OUTCOMES (ONCE PER DAY MAX)
    # =====================================================
    today_start_utc = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    existing_log = ActionHistory.query.filter(
        ActionHistory.store_id == store_id,
        ActionHistory.timestamp >= today_start_utc,
    ).first()

    if pacific_now.hour >= 17 and not existing_log:
        for action in recommended_actions:
            db.session.add(
                ActionHistory(
                    store_id=store_id,
                    action_text=action["text"],  # ✅ FIXED
                    success=improved,
                    dispatch_count=dispatch,
                    inspection_count=inspection,
                    approval_count=approval,
                    service_count=service
                )
            )
        db.session.commit()

    weights_last_updated_today = (
        weights.updated_at.date() == datetime.utcnow().date()
        if weights and weights.updated_at
        else False
    )

    if pacific_now.hour >= 17 and not weights_last_updated_today:
        tune_decision_weights(store_id)
        weights = DecisionWeights.query.filter_by(store_id=store_id).first()
        BASE_WEIGHT = weights.base_weight
        HISTORY_WEIGHT = weights.history_weight
        CONTEXT_WEIGHT = weights.context_weight

    # =====================================================
    # 18. TOP / BOTTOM TECHS
    # =====================================================
    top_techs = (
        db.session.query(
            TeamMember.name,
            func.sum(WorkLog.flat_rate_hours).label("total_hours"),
        )
        .join(WorkLog)
        .join(Team)
        .filter(
            Team.store_id == store_id,
            WorkLog.date >= start_month,
            WorkLog.date <= today,
        )
        .group_by(TeamMember.id)
        .order_by(func.sum(WorkLog.flat_rate_hours).desc())
        .limit(5)
        .all()
    )

    bottom_techs = (
        db.session.query(
            TeamMember.name,
            func.sum(WorkLog.flat_rate_hours).label("total_hours"),
        )
        .join(WorkLog)
        .join(Team)
        .filter(
            Team.store_id == store_id,
            WorkLog.date >= start_month,
            WorkLog.date <= today,
        )
        .group_by(TeamMember.id)
        .order_by(func.sum(WorkLog.flat_rate_hours).asc())
        .limit(5)
        .all()
    )

    # =====================================================
    # 19. WEEKLY FINANCIAL FORECAST
    # =====================================================
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    current_week_dates = f"{start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d')}"

    weekly_financial_total = {
        "total_gross": 0.0,
        "labor_gross": 0.0,
        "parts_gross": 0.0,
        "expected_frh": 0.0,
    }

    if forecast:
        weekly_financial_total["total_gross"] = (forecast.total_gross or 0.0) / 4
        weekly_financial_total["labor_gross"] = (forecast.labor_gross or 0.0) / 4
        weekly_financial_total["parts_gross"] = (forecast.parts_gross or 0.0) / 4
        weekly_financial_total["expected_frh"] = (forecast.expected_frh or 0.0) / 4

    # =====================================================
    # 20. AUDIT STALENESS
    # =====================================================
    store = db.session.get(ManagedStore, store_id)

    routesheet_audit = store.routesheet_audit_timestamp if store else None
    tech_hours_audit = store.tech_hours_audit_timestamp if store else None

    routesheet_audit_stale = True
    tech_hours_audit_stale = True

    if routesheet_audit:
        routesheet_audit_stale = datetime.utcnow() - routesheet_audit > timedelta(hours=24)

    if tech_hours_audit:
        tech_hours_audit_stale = datetime.utcnow() - tech_hours_audit > timedelta(hours=24)

    # =====================================================
    # 21. TODAY NEEDED HOURS TO STAY ON PACE
    # =====================================================
    today_needed_hours = 0.0
    if remaining_work_days > 0:
        today_needed_hours = ((expected_pace_hours - mtd_sold) / remaining_work_days) + daily_goal
    today_needed_hours = max(today_needed_hours, 0)

    # =====================================================
    # 22. TODAY FOCUS
    # =====================================================
    today_focus = generate_today_focus(
        daily_goal,
        today_production,
        forecasted_utilization,
        current_utilization,
        status_counts,
    )

    critical_ros = late_ros[:5]
    remaining_late_count = max(len(late_ros) - 5, 0)

    # --- ACTION PERFORMANCE DASHBOARD ---

    action_stats = (
        db.session.query(
            ActionHistory.action_text,
            func.count(ActionHistory.id),
            func.sum(case((ActionHistory.success.is_(True), 1), else_=0)),
            func.avg(ActionHistory.dispatch_count),
            func.avg(ActionHistory.inspection_count),
            func.avg(ActionHistory.approval_count),
            func.avg(ActionHistory.service_count),
        )
        .filter(ActionHistory.store_id == store_id)
        .group_by(ActionHistory.action_text)
        .all()
    )

    action_performance = []

    for row in action_stats:
        (
            action,
            total,
            successes,
            avg_dispatch,
            avg_inspection,
            avg_approval,
            avg_service
        ) = row

        success_rate = (successes / total) if total else 0

        # --- PERFORMANCE LABEL ---
        if success_rate >= 0.75:
            performance = "🟢 High"
        elif success_rate >= 0.5:
            performance = "🟡 Medium"
        else:
            performance = "🔴 Low"

        # --- CONTEXT DETECTION ---
        context = "General use"

        if avg_approval is not None and avg_service is not None and avg_approval > avg_service:
            context = f"Works best when approvals ({int(avg_approval)}) exceed service load ({int(avg_service)})"

        elif avg_inspection and avg_service and avg_inspection > avg_service * 1.5:
            context = "Best when inspection backlog is high"

        elif avg_dispatch and avg_service and avg_dispatch > avg_service:
            context = "Best when dispatch queue is full"

        # --- BUILD OUTPUT ---
        action_performance.append({
            "action": action,
            "total": total,
            "success_rate": round(success_rate * 100, 1),
            "performance": performance,
            "context": context
        })

    action_perf_map = {
        a["action"]: a
        for a in action_performance
    }

    # Sort best → worst
    action_performance.sort(key=lambda x: x["success_rate"], reverse=True)

    
   

    # =====================================================
    # 23. RENDER
    # =====================================================
    return render_template(
        "home.html",
        title="Executive Dashboard",
        today_date=today.strftime("%A, %B %d"),
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
        mtd_deficit=mtd_deficit,
        deficit_level=deficit_level,
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
        mtd_utilization=mtd_utilization,
        monthly_planned_utilization=monthly_planned_utilization,
        current_utilization=current_utilization,
        forecasted_utilization=forecasted_utilization,
        capacity_gap_hours=capacity_gap_hours,
        capacity_gap_pct=capacity_gap_pct,
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
        remaining_today_hours=remaining_today_hours,
        action_performance=action_performance,
        low_confidence_alert=low_confidence_alert,
        low_confidence_message=low_confidence_message,
        base_weight=BASE_WEIGHT,
        history_weight=HISTORY_WEIGHT,
        context_weight=CONTEXT_WEIGHT,
        mtd_gross=mtd_gross,
        yesterday_gross=yesterday_gross,
        today_appts=today_appts,
        expected_mtd_gross=expected_mtd_gross,
        true_forecast_gross=true_forecast_gross,
        gross_gap=gross_gap,
        forecast_gap=forecast_gap,
        monthly_gross_goal=monthly_gross_goal,
        metrics_entered_today=metrics_entered_today,
        today_needed_gross=today_needed_gross,
        normal_daily_gross=normal_daily_gross,
        appointment_delta=appointment_delta
      
    )

# --- Daily input for performance tracking ---
@main_bp.route("/input-metrics", methods=["GET", "POST"])
@login_required
def input_metrics():

    if request.method == "POST":
        mtd_gross = float(request.form.get("mtd_gross") or 0)
        yesterday_gross = float(request.form.get("yesterday_gross") or 0)
        today_appts = int(request.form.get("today_appts") or 0)

        existing = DailyMetrics.query.filter_by(
            store_id=current_user.store_id,
            date=date.today()
        ).first()

        if existing:
            existing.mtd_gross = mtd_gross
            existing.yesterday_gross = yesterday_gross
            existing.today_appts = today_appts
        else:
            existing = DailyMetrics(
                store_id=current_user.store_id,
                date=date.today(),
                mtd_gross=mtd_gross,
                yesterday_gross=yesterday_gross,
                today_appts=today_appts
            )
            db.session.add(existing)

        db.session.commit()

        return redirect(url_for("main.home"))

    return render_template("input_metrics.html")


from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from extensions import db
from models import (
    RepairOrder,
    WorkLog,
    TeamMember,
    ScheduleEntry,
    FinancialForecast,
    Team,
    ManagedStore,
    DailyMetrics,
)
from sqlalchemy import func
from datetime import date, datetime, timedelta
import pytz
import math
from .schedule import count_workdays, get_holiday_dates

main_bp = Blueprint("main", __name__)


def get_elapsed_work_hours() -> float:
    tz = pytz.timezone("US/Pacific")
    now = datetime.now(tz)

    start = now.replace(hour=7, minute=0, second=0, microsecond=0)
    end = now.replace(hour=17, minute=0, second=0, microsecond=0)

    if now < start:
        return 0.1
    if now > end:
        return 10.0

    elapsed = now - start
    return elapsed.total_seconds() / 3600


def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)


def get_last_workday(target_date: date) -> date:
    target_date = target_date - timedelta(days=1)
    while target_date.weekday() == 6:
        target_date -= timedelta(days=1)
    return target_date


def get_metrics_date(today: date | None = None) -> tuple[date, bool]:
    current_day = today or date.today()
    return get_last_workday(current_day), current_day.weekday() == 6


def get_month_bounds(target_date: date) -> tuple[date, date]:
    start_month = date(target_date.year, target_date.month, 1)
    next_month = (start_month.replace(day=28) + timedelta(days=4)).replace(day=1)
    end_of_month = next_month - timedelta(days=1)
    return start_month, end_of_month


def get_holidays_for_range(start_month: date, end_of_month: date, year: int) -> set:
    holidays = set()
    for month in range(start_month.month, end_of_month.month + 1):
        holidays.update(get_holiday_dates(year, month, month))
    return holidays


def get_workday_summary(metrics_date: date) -> dict:
    start_month, end_of_month = get_month_bounds(metrics_date)
    holidays = get_holidays_for_range(start_month, end_of_month, metrics_date.year)

    elapsed_work_days = count_workdays(start_month, metrics_date, holidays)
    total_work_days = count_workdays(start_month, end_of_month, holidays)
    remaining_work_days = max(total_work_days - elapsed_work_days, 1)

    return {
        "start_month": start_month,
        "end_of_month": end_of_month,
        "elapsed_work_days": elapsed_work_days,
        "total_work_days": total_work_days,
        "remaining_work_days": remaining_work_days,
    }


def get_mtd_sold_hours(store_id: int, start_month: date, metrics_date: date) -> float:
    return (
        db.session.query(func.sum(WorkLog.flat_rate_hours))
        .join(TeamMember)
        .join(Team)
        .filter(
            Team.store_id == store_id,
            WorkLog.date >= start_month,
            WorkLog.date <= metrics_date,
        )
        .scalar()
        or 0
    )


def get_daily_metrics(store_id: int, metrics_date: date) -> dict:
    metrics = DailyMetrics.query.filter_by(
        store_id=store_id,
        date=metrics_date,
    ).first()

    return {
        "record": metrics,
        "today_total_gross": metrics.total_gross if metrics else 0,
        "today_labor_gross": metrics.labor_gross if metrics else 0,
        "today_parts_gross": metrics.parts_gross if metrics else 0,
        "today_sublet_gross": metrics.sublet_gross if metrics else 0,
        "today_appts": metrics.today_appts if metrics else 0,
        "appt_7_day": metrics.appt_7_day if metrics else 0,
    }


def get_forecast_summary(store_id: int, metrics_date: date) -> dict:
    forecast = FinancialForecast.query.filter_by(
        store_id=store_id,
        month=metrics_date.month,
        year=metrics_date.year,
    ).first()

    projected_gross = forecast.total_gross if forecast else 0
    monthly_frh_goal = (
        forecast.expected_frh
        if forecast and forecast.expected_frh and forecast.expected_frh > 0
        else 0
    )

    return {
        "forecast": forecast,
        "projected_gross": projected_gross,
        "monthly_frh_goal": monthly_frh_goal,
    }


def get_mtd_gross_summary(store_id: int, start_month: date, metrics_date: date) -> dict:
    latest_metrics = (
        DailyMetrics.query.filter(
            DailyMetrics.store_id == store_id,
            DailyMetrics.date >= start_month,
            DailyMetrics.date <= metrics_date,
        )
        .order_by(DailyMetrics.date.desc())
        .first()
    )

    if not latest_metrics:
        return {
            "mtd_labor_gross": 0.0,
            "mtd_total_gross": 0.0,
            "latest_metrics": None,
        }

    return {
        "mtd_labor_gross": float(latest_metrics.labor_gross or 0),
        "mtd_total_gross": float(latest_metrics.total_gross or 0),
        "latest_metrics": latest_metrics,
    }

def calculate_expected_mtd_gross(projected_gross: float, elapsed_work_days: int, total_work_days: int) -> float:
    if total_work_days <= 0:
        return 0
    return projected_gross * (elapsed_work_days / total_work_days)


def calculate_blended_gph(
    mtd_labor_gross: float,
    mtd_sold_hours: float,
    forecast: FinancialForecast | None,
    default_gph: float = 120,
) -> float:
    actual_gph = (mtd_labor_gross / mtd_sold_hours) if mtd_sold_hours > 0 else None

    forecast_gph = (
        forecast.labor_gross / forecast.expected_frh
        if forecast and forecast.expected_frh > 0
        else default_gph
    )

    blended_gph = (actual_gph * 0.7) + (forecast_gph * 0.3) if actual_gph else forecast_gph
    return max(min(blended_gph, 200), 80)


def calculate_hours_model(
    projected_gross: float,
    total_work_days: int,
    gph: float,
    mtd_deficit: float,
    remaining_work_days: int,
) -> dict:
    normal_daily_gross = (projected_gross / total_work_days) if total_work_days > 0 else 0
    daily_base_hours = (normal_daily_gross / gph) if gph > 0 else 0
    mtd_deficit_hours = (mtd_deficit / gph) if gph > 0 else 0
    daily_recovery_hours = (mtd_deficit_hours / remaining_work_days) if remaining_work_days > 0 else 0

    severity = abs(mtd_deficit) / projected_gross if projected_gross > 0 else 0

    if severity < 0.05:
        cap_pct = 0.25
    elif severity < 0.10:
        cap_pct = 0.50
    else:
        cap_pct = 1.0

    recovery_cap = daily_base_hours * cap_pct
    daily_recovery_hours = max(min(daily_recovery_hours, recovery_cap), -recovery_cap)
    today_target_hours = daily_base_hours + daily_recovery_hours

    base_daily_gross = normal_daily_gross
    recovery_daily_gross = daily_recovery_hours * gph if gph > 0 else 0
    updated_daily_gross = today_target_hours * gph if gph > 0 else 0

    return {
        "normal_daily_gross": normal_daily_gross,
        "daily_base_hours": daily_base_hours,
        "mtd_deficit_hours": mtd_deficit_hours,
        "daily_recovery_hours": daily_recovery_hours,
        "today_target_hours": today_target_hours,
        "base_daily_gross": base_daily_gross,
        "recovery_daily_gross": recovery_daily_gross,
        "updated_daily_gross": updated_daily_gross,
    }


def calculate_mtd_hours_tracking(daily_base_hours: float, elapsed_work_days: int, mtd_sold_hours: float) -> dict:
    mtd_target_hours = daily_base_hours * elapsed_work_days
    mtd_hours_gap = mtd_sold_hours - mtd_target_hours

    return {
        "mtd_target_hours": mtd_target_hours,
        "mtd_hours_gap": mtd_hours_gap,
    }


def get_total_ros_mtd(store_id: int, start_month: date, metrics_date: date) -> int:
    return (
        db.session.query(func.count(func.distinct(WorkLog.ro_number)))
        .join(TeamMember, TeamMember.id == WorkLog.team_member_id)
        .join(Team, Team.id == TeamMember.team_id)
        .filter(
            Team.store_id == store_id,
            WorkLog.date >= start_month,
            WorkLog.date <= metrics_date,
            WorkLog.ro_number.isnot(None),
            WorkLog.ro_number != "",
        )
        .scalar()
        or 0
    )


def calculate_avg_hours_per_ro(mtd_sold_hours: float, total_ros_mtd: int) -> float:
    raw_avg_hours = (mtd_sold_hours / total_ros_mtd) if total_ros_mtd > 0 else 2
    return max(1.5, min(raw_avg_hours, 5.0))


def calculate_appointment_summary(
    today_target_hours: float,
    adjusted_wip_hours: float,
    avg_hours_per_ro: float,
    today_appts: int,
    appt_7_day: int,
) -> dict:
    additional_hours_needed = max(today_target_hours - adjusted_wip_hours, 0)

    needed_appointments = (
        math.ceil(additional_hours_needed / avg_hours_per_ro)
        if avg_hours_per_ro > 0
        else 0
    )

    appointment_delta = today_appts - needed_appointments
    appt_7_day_delta = appt_7_day - (needed_appointments * 6)

    cp_needed = math.ceil(needed_appointments * 0.6)
    wp_needed = max(needed_appointments - cp_needed, 0)

    return {
        "additional_hours_needed": round(additional_hours_needed, 1),
        "needed_appointments": needed_appointments,
        "appointment_delta": appointment_delta,
        "appt_7_day_delta": appt_7_day_delta,
        "cp_needed": cp_needed,
        "wp_needed": wp_needed,
    }

def get_open_repair_orders(store_id: int) -> list[RepairOrder]:
    return RepairOrder.query.filter(
        RepairOrder.store_id == store_id,
        RepairOrder.status != "Closed",
    ).all()


def build_status_counts(repair_orders: list[RepairOrder]) -> dict:
    tracked_statuses = [
        "Dispatch",
        "Inspection",
        "Approval",
        "Parts",
        "Service",
        "Warranty",
        "Ready",
    ]
    counts = {status: 0 for status in tracked_statuses}

    for ro in repair_orders:
        if ro.status in counts:
            counts[ro.status] += 1

    return counts


def calculate_wip_capacity(avg_hours_per_ro: float, repair_orders: list[RepairOrder], today_target_hours: float) -> dict:
    status_counts = build_status_counts(repair_orders)

    service_count = status_counts["Service"]
    dispatch_count = status_counts["Dispatch"]
    parts_count = status_counts["Parts"]
    ready_count = status_counts["Ready"]
    warranty_count = status_counts["Warranty"]

    service_weight = 0.8
    dispatch_weight = 0.7
    parts_weight = 0.2
    ready_weight = 1.0
    warranty_weight = 1.0
    same_day_conversion_factor = 0.65

    weighted_ros = (
        (service_count * service_weight)
        + (dispatch_count * dispatch_weight)
        + (parts_count * parts_weight)
        + (ready_count * ready_weight)
        + (warranty_count * warranty_weight)
    )

    adjusted_wip_hours = weighted_ros * (avg_hours_per_ro * same_day_conversion_factor)
    capacity_gap = adjusted_wip_hours - today_target_hours

    return {
        "status_counts": status_counts,
        "adjusted_wip_hours": adjusted_wip_hours,
        "capacity_gap": capacity_gap,
        "wip_debug": {
            "service_weight": service_weight,
            "dispatch_weight": dispatch_weight,
            "parts_weight": parts_weight,
            "ready_weight": ready_weight,
            "warranty_weight": warranty_weight,
            "same_day_conversion_factor": same_day_conversion_factor,
            "weighted_ros": weighted_ros,
        },
    }

def generate_today_focus(
    daily_goal,
    today_production,
    forecasted_utilization,
    current_utilization,
    status_counts,
):
    gap = max(daily_goal - today_production, 0)
    ros_needed = math.ceil(gap / 2) if gap > 0 else 0

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
        }

    remaining_hours = max(10 - get_elapsed_work_hours(), 1)
    pace_needed = round(gap / remaining_hours, 1)

    dispatch = status_counts.get("Dispatch", 0)
    inspection = status_counts.get("Inspection", 0)
    approval = status_counts.get("Approval", 0)
    service = status_counts.get("Service", 0)

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
        blocker = "Low technician output vs target"
        actions = [
            "Check technician productivity",
            "Intervene with slow or idle techs",
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
    }


def get_top_techs(store_id: int, start_month: date, metrics_date: date, limit: int = 5) -> list[dict]:
    rows = (
        db.session.query(
            TeamMember.id.label("team_member_id"),
            TeamMember.name.label("name"),
            func.sum(WorkLog.flat_rate_hours).label("total_hours"),
        )
        .join(TeamMember)
        .join(Team)
        .filter(
            Team.store_id == store_id,
            WorkLog.date >= start_month,
            WorkLog.date <= metrics_date,
        )
        .group_by(TeamMember.id, TeamMember.name)
        .order_by(func.sum(WorkLog.flat_rate_hours).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "team_member_id": row.team_member_id,
            "name": (row.name or "").strip(),
            "total_hours": float(row.total_hours or 0),
        }
        for row in rows
        if (row.name or "").strip() and (row.name or "").strip().upper() not in {"TBD", "NONE", "UNASSIGNED"}
    ]


def get_scheduled_workdays_map(store_id: int, start_month: date, metrics_date: date) -> dict[int, int]:
    rows = (
        db.session.query(
            ScheduleEntry.team_member_id,
            func.count(ScheduleEntry.id).label("scheduled_days"),
        )
        .join(TeamMember, TeamMember.id == ScheduleEntry.team_member_id)
        .join(Team, Team.id == TeamMember.team_id)
        .filter(
            Team.store_id == store_id,
            ScheduleEntry.date >= start_month,
            ScheduleEntry.date <= metrics_date,
            ScheduleEntry.schedule_type == "WORK",
        )
        .group_by(ScheduleEntry.team_member_id)
        .all()
    )

    return {row.team_member_id: int(row.scheduled_days or 0) for row in rows}


def get_actual_hours_map(store_id: int, start_month: date, metrics_date: date) -> dict[int, float]:
    rows = (
        db.session.query(
            WorkLog.team_member_id,
            func.sum(WorkLog.flat_rate_hours).label("total_hours"),
        )
        .join(TeamMember, TeamMember.id == WorkLog.team_member_id)
        .join(Team, Team.id == TeamMember.team_id)
        .filter(
            Team.store_id == store_id,
            WorkLog.date >= start_month,
            WorkLog.date <= metrics_date,
        )
        .group_by(WorkLog.team_member_id)
        .all()
    )

    return {row.team_member_id: float(row.total_hours or 0) for row in rows}


def get_techs_below_pace(store_id: int, start_month: date, metrics_date: date) -> list[dict]:
    team_members = (
        TeamMember.query
        .join(Team)
        .filter(Team.store_id == store_id)
        .all()
    )

    scheduled_days_map = get_scheduled_workdays_map(store_id, start_month, metrics_date)
    actual_hours_map = get_actual_hours_map(store_id, start_month, metrics_date)

    below = []

    for tech in team_members:
        name = (tech.name or "").strip()
        if not name or name.upper() in {"TBD", "NONE", "UNASSIGNED"}:
            continue

        daily_objective = float(tech.daily_production_objective or 0)
        scheduled_days = int(scheduled_days_map.get(tech.id, 0))
        actual_hours = float(actual_hours_map.get(tech.id, 0))

        if daily_objective <= 0 or scheduled_days <= 0:
            continue

        target_hours = daily_objective * scheduled_days
        gap_hours = target_hours - actual_hours

        if gap_hours < 2.0:
            continue

        below.append(
            {
                "name": name,
                "actual_hours": actual_hours,
                "target_hours": target_hours,
                "gap_hours": gap_hours,
                "scheduled_days": scheduled_days,
                "daily_objective": daily_objective,
            }
        )

    below.sort(key=lambda item: item["gap_hours"], reverse=True)
    return below[:10]


def get_critical_ros(repair_orders: list[RepairOrder], limit: int = 5) -> tuple[list[dict], int]:
    overdue_ros = []

    for ro in repair_orders:
        promised_time = getattr(ro, "promised_time", None)
        if not promised_time:
            continue

        try:
            compare_now = datetime.now(promised_time.tzinfo) if promised_time.tzinfo else datetime.now()
            is_late = promised_time < compare_now
        except Exception:
            continue

        if not is_late:
            continue

        late_delta = compare_now - promised_time
        late_minutes = max(int(late_delta.total_seconds() // 60), 0)

        if late_minutes < 60:
            late_label = f"{late_minutes} min late"
        else:
            hours = late_minutes // 60
            minutes = late_minutes % 60
            if minutes == 0:
                late_label = f"{hours} hr late"
            else:
                late_label = f"{hours} hr {minutes} min late"

        overdue_ros.append(
            {
                "ro_number": ro.ro_number,
                "customer_name": ro.customer_name,
                "promised_time": promised_time,
                "is_late": True,
                "is_due_soon": False,
                "late_label": late_label,
            }
        )

    overdue_ros.sort(key=lambda ro: ro["promised_time"] or datetime.max)

    critical = overdue_ros[:limit]
    remaining = max(len(overdue_ros) - len(critical), 0)

    return critical, remaining

def get_sync_status(timestamp: datetime | None, stale_hours: int = 24) -> dict:
    pacific = pytz.timezone("US/Pacific")

    if not timestamp:
        return {
            "timestamp": None,
            "is_stale": True,
            "label": "Never",
        }

    if timestamp.tzinfo is None:
        timestamp = pytz.utc.localize(timestamp)

    local_timestamp = timestamp.astimezone(pacific)
    now_local = datetime.now(pacific)
    age = now_local - local_timestamp
    is_stale = age > timedelta(hours=stale_hours)

    return {
        "timestamp": local_timestamp,
        "is_stale": is_stale,
        "label": local_timestamp.strftime("%b %d, %I:%M %p"),
    }

def get_recommended_tool(issue: str) -> dict:
    tool_map = {
        "Pacing Risk": {
            "label": "Open Pace Recovery Calculator",
            "endpoint": "calculators.pace_recovery_calculator",
        },
        "Low Utilization": {
            "label": "Open Appointment Lift Calculator",
            "endpoint": "calculators.appointment_lift_calculator",
        },
        "Low Production Output": {
            "label": "Open Pace Recovery Calculator",
            "endpoint": "calculators.pace_recovery_calculator",
        },
        "Dispatch Bottleneck": {
            "label": "Open Route Sheet",
            "endpoint": "routesheet.view_sheet",
        },
        "Inspection Backlog": {
            "label": "Open Route Sheet",
            "endpoint": "routesheet.view_sheet",
        },
        "Approval Bottleneck": {
            "label": "Open Route Sheet",
            "endpoint": "routesheet.view_sheet",
        },
        "Underloaded Service": {
            "label": "Open Route Sheet",
            "endpoint": "routesheet.view_sheet",
        },
        "No Active Work": {
            "label": "Open Route Sheet",
            "endpoint": "routesheet.view_sheet",
        },
        "Monday Readiness": {
            "label": "Open Route Sheet",
            "endpoint": "routesheet.view_sheet",
        },
    }

    return tool_map.get(
        issue,
        {
            "label": "Open CP Gross Profit Calculator",
            "endpoint": "calculators.cpgp_calculator",
        },
    )

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
    metrics_date, is_sunday = get_metrics_date()

    store = ManagedStore.query.get(store_id)

    workday_data = get_workday_summary(metrics_date)
    start_month = workday_data["start_month"]
    elapsed_work_days = workday_data["elapsed_work_days"]
    total_work_days = workday_data["total_work_days"]
    remaining_work_days = workday_data["remaining_work_days"]

    mtd_sold = get_mtd_sold_hours(store_id, start_month, metrics_date)

    daily_metrics_data = get_daily_metrics(store_id, metrics_date)
    today_total_gross = daily_metrics_data["today_total_gross"]
    today_labor_gross = daily_metrics_data["today_labor_gross"]
    today_parts_gross = daily_metrics_data["today_parts_gross"]
    today_sublet_gross = daily_metrics_data["today_sublet_gross"]
    today_appts = daily_metrics_data["today_appts"]
    appt_7_day = daily_metrics_data["appt_7_day"]

    forecast_data = get_forecast_summary(store_id, metrics_date)
    forecast = forecast_data["forecast"]
    projected_gross = forecast_data["projected_gross"]
    monthly_frh_goal = forecast_data["monthly_frh_goal"]

    gross_data = get_mtd_gross_summary(store_id, start_month, metrics_date)
    mtd_labor_gross = gross_data["mtd_labor_gross"]
    mtd_total_gross = gross_data["mtd_total_gross"]

    expected_mtd_gross = calculate_expected_mtd_gross(
        projected_gross=projected_gross,
        elapsed_work_days=elapsed_work_days,
        total_work_days=total_work_days,
    )
    mtd_deficit = expected_mtd_gross - mtd_total_gross

    metrics_days_count = db.session.query(func.count(DailyMetrics.id)).filter(
        DailyMetrics.store_id == store_id,
        DailyMetrics.date >= start_month,
        DailyMetrics.date <= metrics_date,
        DailyMetrics.total_gross > 0
    ).scalar() or 0

    projected_month_end_gross = (
        (mtd_total_gross / elapsed_work_days) * total_work_days
        if elapsed_work_days > 0
        else 0
    )

    projected_month_end_frh = (
        (mtd_sold / elapsed_work_days) * total_work_days
        if elapsed_work_days > 0
        else 0
    )

    gph = calculate_blended_gph(
        mtd_labor_gross=mtd_labor_gross,
        mtd_sold_hours=mtd_sold,
        forecast=forecast,
    )

    if monthly_frh_goal <= 0:
        monthly_frh_goal = projected_gross / gph if gph > 0 else 0

    expected_pace_hours = (
        monthly_frh_goal * (elapsed_work_days / total_work_days)
        if total_work_days > 0
        else 0
    )

    hours_model = calculate_hours_model(
        projected_gross=projected_gross,
        total_work_days=total_work_days,
        gph=gph,
        mtd_deficit=mtd_deficit,
        remaining_work_days=remaining_work_days,
    )
    normal_daily_gross = hours_model["normal_daily_gross"]
    daily_goal = hours_model["today_target_hours"]
    today_needed_hours = hours_model["today_target_hours"]
    daily_base_hours = hours_model["daily_base_hours"]
    daily_recovery_hours = hours_model["daily_recovery_hours"]
    base_daily_gross = hours_model["base_daily_gross"]
    recovery_daily_gross = hours_model["recovery_daily_gross"]
    updated_daily_gross = hours_model["updated_daily_gross"]

    mtd_hours_tracking = calculate_mtd_hours_tracking(
        daily_base_hours=daily_base_hours,
        elapsed_work_days=elapsed_work_days,
        mtd_sold_hours=mtd_sold,
    )
    mtd_target_hours = mtd_hours_tracking["mtd_target_hours"]
    mtd_hours_gap = mtd_hours_tracking["mtd_hours_gap"]

    total_ros_mtd = get_total_ros_mtd(store_id, start_month, metrics_date)
    avg_hours_per_ro = calculate_avg_hours_per_ro(mtd_sold, total_ros_mtd)

    open_repair_orders = get_open_repair_orders(store_id)
    wip_data = calculate_wip_capacity(
        avg_hours_per_ro=avg_hours_per_ro,
        repair_orders=open_repair_orders,
        today_target_hours=today_needed_hours,
    )
    status_counts = wip_data["status_counts"]
    adjusted_wip_hours = wip_data["adjusted_wip_hours"]
    capacity_gap = wip_data["capacity_gap"]
    wip_debug = wip_data["wip_debug"]

    appointment_data = calculate_appointment_summary(
        today_target_hours=today_needed_hours,
        adjusted_wip_hours=adjusted_wip_hours,
        avg_hours_per_ro=avg_hours_per_ro,
        today_appts=today_appts,
        appt_7_day=appt_7_day,
    )
    needed_appointments = appointment_data["needed_appointments"]
    appointment_delta = appointment_data["appointment_delta"]
    appt_7_day_delta = appointment_data["appt_7_day_delta"]
    cp_needed = appointment_data["cp_needed"]
    wp_needed = appointment_data["wp_needed"]
    additional_hours_needed = appointment_data["additional_hours_needed"]

    current_loaded_hours = adjusted_wip_hours
    remaining_hours_today = max(today_needed_hours - current_loaded_hours, 0)
    on_pace = current_loaded_hours >= today_needed_hours

    current_utilization = (
        (current_loaded_hours / today_needed_hours) * 100
        if today_needed_hours > 0
        else 0
    )
    current_utilization = clamp(current_utilization, 0, 150)

    today_focus = generate_today_focus(
        daily_goal=today_needed_hours,
        today_production=current_loaded_hours,
        forecasted_utilization=100,
        current_utilization=current_utilization,
        status_counts=status_counts,
    )

    top_techs = get_top_techs(store_id, start_month, metrics_date)
    techs_below_pace = get_techs_below_pace(
        store_id=store_id,
        start_month=start_month,
        metrics_date=metrics_date,
    )

    critical_ros, remaining_late_count = get_critical_ros(open_repair_orders)

    routesheet_sync = get_sync_status(store.routesheet_audit_timestamp if store else None)
    tech_hours_sync = get_sync_status(store.tech_hours_audit_timestamp if store else None)

    if is_sunday:
        needed_appointments = 0
        cp_needed = 0
        wp_needed = 0
        appointment_delta = 0
        appt_7_day_delta = 0

        today_needed_hours = 0
        daily_goal = 0
        updated_daily_gross = 0
        recovery_daily_gross = 0
        daily_recovery_hours = 0

        current_loaded_hours = 0
        remaining_hours_today = 0
        adjusted_wip_hours = 0
        capacity_gap = 0
        on_pace = True

        today_focus = {
            "issue": "Monday Readiness",
            "message": "Sunday view is for readiness, not live production pacing.",
            "gap": 0,
            "ros_needed": 0,
            "pace_needed": 0,
            "actions": [
                "Review dispatch backlog",
                "Confirm Monday appointment load",
                "Prepare carryover and ready-to-close work",
            ],
        }
    day_label = "Sunday - Monday Readiness" if is_sunday else "Today"
    recommended_tool = get_recommended_tool(today_focus["issue"])
    print("----- DAILY METRICS DEBUG -----")
    print("latest_metrics_date:", gross_data["latest_metrics"].date if gross_data["latest_metrics"] else None)
    print("mtd_labor_gross:", mtd_labor_gross)
    print("mtd_total_gross:", mtd_total_gross)
    print("today_total_gross:", today_total_gross)
    print("today_labor_gross:", today_labor_gross)
    print("today_parts_gross:", today_parts_gross)
    print("today_sublet_gross:", today_sublet_gross)
    print("-------------------------------")
    return render_template(
        "home.html",
        projected_gross=projected_gross,
        projected_month_end_gross=projected_month_end_gross,
        projected_month_end_frh=projected_month_end_frh,
        monthly_frh_goal=monthly_frh_goal,
        expected_pace_hours=expected_pace_hours,
        mtd_total_gross=mtd_total_gross,
        expected_mtd_gross=expected_mtd_gross,
        mtd_deficit=mtd_deficit,
        mtd_target_hours=mtd_target_hours,
        mtd_sold=mtd_sold,
        mtd_hours_gap=mtd_hours_gap,
        today_target_hours=today_needed_hours,
        today_needed_hours=today_needed_hours,
        today_total_gross=today_total_gross,
        today_labor_gross=today_labor_gross,
        today_parts_gross=today_parts_gross,
        today_sublet_gross=today_sublet_gross,
        today_appts=today_appts,
        appointment_delta=appointment_delta,
        appt_7_day=appt_7_day,
        appt_7_day_delta=appt_7_day_delta,
        needed_appointments=needed_appointments,
        cp_needed=cp_needed,
        wp_needed=wp_needed,
        capacity_gap=capacity_gap,
        adjusted_wip_hours=adjusted_wip_hours,
        current_loaded_hours=current_loaded_hours,
        remaining_hours_today=remaining_hours_today,
        avg_hours_per_ro=avg_hours_per_ro,
        normal_daily_gross=normal_daily_gross,
        daily_goal=daily_goal,
        daily_base_hours=daily_base_hours,
        daily_recovery_hours=daily_recovery_hours,
        base_daily_gross=base_daily_gross,
        recovery_daily_gross=recovery_daily_gross,
        updated_daily_gross=updated_daily_gross,
        gph=gph,
        today_focus=today_focus,
        status_counts=status_counts,
        top_techs=top_techs,
        techs_below_pace=techs_below_pace,
        critical_ros=critical_ros,
        remaining_late_count=remaining_late_count,
        routesheet_sync=routesheet_sync,
        tech_hours_sync=tech_hours_sync,
        on_pace=on_pace,
        is_sunday=is_sunday,
        day_label=day_label,
        metrics_date=metrics_date,
        wip_debug=wip_debug,
        recommended_tool=recommended_tool,
        
    )


@main_bp.route("/input-metrics", methods=["GET", "POST"])
@login_required
def input_metrics():
    metrics_date = get_last_workday(date.today())

    if request.method == "POST":
        labor_gross = float(request.form.get("labor_gross") or 0)
        parts_gross = float(request.form.get("parts_gross") or 0)
        sublet_gross = float(request.form.get("sublet_gross") or 0)
        total_gross = labor_gross + parts_gross + sublet_gross
        cp_ros_mtd = int(request.form.get("cp_ros_mtd") or 0)

        today_appts = int(request.form.get("today_appts") or 0)
        appt_7_day = int(request.form.get("appt_7_day") or 0)

        metrics = DailyMetrics.query.filter_by(
            store_id=current_user.store_id,
            date=metrics_date,
        ).first()

        if not metrics:
            metrics = DailyMetrics(
                store_id=current_user.store_id,
                date=metrics_date,
            )
            db.session.add(metrics)

        metrics.labor_gross = labor_gross
        metrics.parts_gross = parts_gross
        metrics.sublet_gross = sublet_gross
        metrics.total_gross = total_gross
        metrics.cp_ros_mtd = cp_ros_mtd
        metrics.today_appts = today_appts
        metrics.appt_7_day = appt_7_day

        db.session.commit()

        flash("Daily metrics saved successfully", "success")
        return redirect(url_for("main.home"))

    metrics = DailyMetrics.query.filter_by(
        store_id=current_user.store_id,
        date=metrics_date,
    ).first()

    return render_template(
        "input_metrics.html",
        metrics=metrics,
        metrics_date=metrics_date,
    )
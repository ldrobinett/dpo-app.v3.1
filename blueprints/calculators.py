
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import func

from extensions import db
from models import (
    DailyMetrics,
    FinancialForecast,
    FinancialInputs,
    RepairOrder,
    ScheduleEntry,
    Team,
    TeamMember,
    TeamSchedule,
    WorkLog,
)
from forms import (
    MPICalculatorForm,
    ApptCalculatorForm,
    CPGPOpportunityForm,
    CapacityOpportunityForm,
    PaceRecoveryCalculatorForm,
    AppointmentLiftCalculatorForm,
)
from datetime import date, datetime, timedelta
import calendar
import math

calculators_bp = Blueprint("calculators", __name__)


def safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value if value is not None else default)
    except (TypeError, ValueError):
        return default


def get_reporting_date() -> date:
    """
    Uses previous workday reporting logic.
    Sundays are skipped.
    """
    today = date.today()
    reporting_date = today - timedelta(days=1)

    while reporting_date.weekday() == 6:
        reporting_date -= timedelta(days=1)

    return reporting_date


def count_workdays(start_date: date, end_date: date) -> int:
    """
    Counts workdays Monday-Saturday.
    Sundays are excluded.
    """
    if start_date > end_date:
        return 0

    day_count = 0
    current = start_date
    while current <= end_date:
        if current.weekday() != 6:
            day_count += 1
        current += timedelta(days=1)

    return day_count


def get_month_boundaries(target_date: date) -> tuple[date, date]:
    start_date = date(target_date.year, target_date.month, 1)
    last_day = calendar.monthrange(target_date.year, target_date.month)[1]
    end_date = date(target_date.year, target_date.month, last_day)
    return start_date, end_date


def get_latest_daily_metrics(store_id: int, start_date: date, end_date: date) -> DailyMetrics | None:
    return (
        DailyMetrics.query.filter(
            DailyMetrics.store_id == store_id,
            DailyMetrics.date >= start_date,
            DailyMetrics.date <= end_date,
        )
        .order_by(DailyMetrics.date.desc())
        .first()
    )


def get_store_forecast(store_id: int, target_date: date) -> FinancialForecast | None:
    return FinancialForecast.query.filter_by(
        store_id=store_id,
        month=target_date.month,
        year=target_date.year,
    ).first()


def get_shop_stats(store_id: int) -> dict:
    """
    Shared finance/staffing defaults used across calculators.
    """
    stats = {
        "tech_count": 0,
        "proficiency": 0.0,
        "elr": 0.0,
        "labor_margin": 0.0,
        "parts_ratio": 0.0,
        "parts_margin": 0.0,
        "unapplied": 0.0,
        "work_days": 21.0,
    }

    inputs = FinancialInputs.query.filter(FinancialInputs.user_id == current_user.id).first()
    if inputs:
        stats["elr"] = safe_float(inputs.effective_labor_rate)
        stats["labor_margin"] = safe_float(inputs.labor_margin)
        stats["parts_ratio"] = safe_float(inputs.parts_to_labor_ratio)
        stats["parts_margin"] = safe_float(inputs.parts_margin)
        stats["unapplied"] = safe_float(inputs.unapplied_time_cost)

    techs = TeamMember.query.join(Team).filter(Team.store_id == store_id).all()
    stats["tech_count"] = len(techs)

    if techs:
        total_dpo = sum(safe_float(tech.daily_production_objective) for tech in techs)
        total_scheduled_hours = 0.0

        for tech in techs:
            daily_hours = 8.0

            if tech.team:
                schedules = TeamSchedule.query.filter_by(team_id=tech.team.id).all()
                if schedules:
                    weekly_hours = 0.0

                    for schedule in schedules:
                        start_dt = datetime.combine(date.min, schedule.start_time)
                        end_dt = datetime.combine(date.min, schedule.end_time)
                        duration = (end_dt - start_dt).total_seconds() / 3600

                        if schedule.lunch_start and schedule.lunch_end:
                            lunch_start = datetime.combine(date.min, schedule.lunch_start)
                            lunch_end = datetime.combine(date.min, schedule.lunch_end)
                            duration -= (lunch_end - lunch_start).total_seconds() / 3600

                        weekly_hours += duration

                    if weekly_hours > 0:
                        daily_hours = weekly_hours / 5.0

            total_scheduled_hours += daily_hours

        if total_scheduled_hours > 0:
            stats["proficiency"] = (total_dpo / total_scheduled_hours) * 100.0

    reporting_date = get_reporting_date()
    start_date, end_date = get_month_boundaries(reporting_date)

    total_scheduled_days = (
        ScheduleEntry.query.join(TeamMember).join(Team).filter(
            Team.store_id == store_id,
            ScheduleEntry.date >= start_date,
            ScheduleEntry.date <= end_date,
            ScheduleEntry.schedule_type == "WORK",
        ).count()
    )

    if stats["tech_count"] > 0:
        avg_days = total_scheduled_days / stats["tech_count"]
        if avg_days > 0:
            stats["work_days"] = avg_days

    return stats


def get_current_month_snapshot(store_id: int) -> dict:
    """
    Shared current-month snapshot used to prefill all calculators.
    Assumes DailyMetrics gross values are entered as MTD values.
    """
    reporting_date = get_reporting_date()
    start_date, end_date = get_month_boundaries(reporting_date)

    latest_metrics = get_latest_daily_metrics(store_id, start_date, reporting_date)
    forecast = get_store_forecast(store_id, reporting_date)
    shop_stats = get_shop_stats(store_id)

    mtd_actual_frh = (
        db.session.query(func.sum(WorkLog.flat_rate_hours))
        .join(TeamMember)
        .join(Team)
        .filter(
            Team.store_id == store_id,
            WorkLog.date >= start_date,
            WorkLog.date <= reporting_date,
        )
        .scalar()
        or 0.0
    )

    ro_count_mtd = (
        db.session.query(func.count(func.distinct(WorkLog.ro_number)))
        .join(TeamMember)
        .join(Team)
        .filter(
            Team.store_id == store_id,
            WorkLog.date >= start_date,
            WorkLog.date <= reporting_date,
            WorkLog.ro_number.isnot(None),
            WorkLog.ro_number != "",
        )
        .scalar()
        or 0
    )

    mtd_total_gross = safe_float(latest_metrics.total_gross) if latest_metrics else 0.0
    mtd_labor_gross = safe_float(latest_metrics.labor_gross) if latest_metrics else 0.0
    mtd_parts_gross = safe_float(latest_metrics.parts_gross) if latest_metrics else 0.0
    mtd_sublet_gross = safe_float(latest_metrics.sublet_gross) if latest_metrics else 0.0
    mtd_cp_ros = int(latest_metrics.cp_ros_mtd or 0) if latest_metrics else 0

    monthly_forecast_gross = safe_float(forecast.total_gross) if forecast else 0.0
    monthly_frh_goal = safe_float(forecast.expected_frh) if forecast else 0.0

    elapsed_workdays = count_workdays(start_date, reporting_date)
    total_workdays = count_workdays(start_date, end_date)
    remaining_workdays = max(total_workdays - elapsed_workdays, 1)

    avg_hours_per_ro = mtd_actual_frh / ro_count_mtd if ro_count_mtd > 0 else 2.0
    avg_hours_per_ro = max(1.0, round(avg_hours_per_ro, 1))

    avg_gross_per_ro = mtd_total_gross / ro_count_mtd if ro_count_mtd > 0 else 0.0
    if avg_gross_per_ro <= 0:
        avg_gross_per_ro = round(shop_stats["elr"] * avg_hours_per_ro, 0) if shop_stats["elr"] > 0 else 300.0

    current_open_ros = (
        RepairOrder.query.filter(
            RepairOrder.store_id == store_id,
            RepairOrder.status != "Closed",
        ).count()
    )

    projected_month_end_gross = (
        (mtd_total_gross / elapsed_workdays) * total_workdays if elapsed_workdays > 0 else 0.0
    )
    projected_month_end_frh = (
        (mtd_actual_frh / elapsed_workdays) * total_workdays if elapsed_workdays > 0 else 0.0
    )
    projected_month_end_cp_ros = (
    (mtd_cp_ros / elapsed_workdays) * total_workdays
    if elapsed_workdays > 0 and mtd_cp_ros > 0
    else 0.0
)
    return {
        "reporting_date": reporting_date,
        "month_start": start_date,
        "month_end": end_date,
        "elapsed_workdays": elapsed_workdays,
        "total_workdays": total_workdays,
        "remaining_workdays": remaining_workdays,
        "latest_metrics": latest_metrics,
        "forecast": forecast,
        "shop_stats": shop_stats,
        "mtd_total_gross": mtd_total_gross,
        "mtd_labor_gross": mtd_labor_gross,
        "mtd_parts_gross": mtd_parts_gross,
        "mtd_sublet_gross": mtd_sublet_gross,
        "mtd_cp_ros": mtd_cp_ros,
        "monthly_forecast_gross": monthly_forecast_gross,
        "monthly_frh_goal": monthly_frh_goal,
        "mtd_actual_frh": mtd_actual_frh,
        "ro_count_mtd": ro_count_mtd,
        "avg_hours_per_ro": avg_hours_per_ro,
        "avg_gross_per_ro": avg_gross_per_ro,
        "current_open_ros": current_open_ros,
        "projected_month_end_gross": projected_month_end_gross,
        "projected_month_end_frh": projected_month_end_frh,
        "projected_month_end_cp_ros": projected_month_end_cp_ros,
    }


@calculators_bp.route("/calculators/mpi", methods=["GET", "POST"])
@login_required
def mpi_calculator():
    form = MPICalculatorForm()

    if request.method == "GET":
        snapshot = get_current_month_snapshot(current_user.store_id)
        stats = snapshot["shop_stats"]

        form.effective_labor_rate.data = stats["elr"]
        form.labor_gross_margin.data = stats["labor_margin"]
        form.parts_to_labor_ratio.data = stats["parts_ratio"]
        form.parts_gross_margin.data = stats["parts_margin"]

        if snapshot["projected_month_end_cp_ros"] > 0:
            form.monthly_cp_ros.data = int(round(snapshot["projected_month_end_cp_ros"]))
        elif snapshot["mtd_cp_ros"] > 0:
            form.monthly_cp_ros.data = int(snapshot["mtd_cp_ros"])
        elif snapshot["ro_count_mtd"] > 0:
            form.monthly_cp_ros.data = int(snapshot["ro_count_mtd"])
        elif stats["tech_count"] > 0:
            daily_cap_hours = stats["tech_count"] * 8 * (stats["proficiency"] / 100.0)
            monthly_cap_hours = daily_cap_hours * snapshot["total_workdays"]
            form.monthly_cp_ros.data = int(monthly_cap_hours / max(snapshot["avg_hours_per_ro"], 1.0))
        else:
            form.monthly_cp_ros.data = 0

    results = None
    if form.validate_on_submit():
        elr = safe_float(form.effective_labor_rate.data)
        tenths = safe_float(form.tenths_increase.data)
        labor_margin = safe_float(form.labor_gross_margin.data) / 100.0
        parts_labor_ratio = safe_float(form.parts_to_labor_ratio.data)
        parts_margin = safe_float(form.parts_gross_margin.data) / 100.0
        monthly_ros = int(form.monthly_cp_ros.data or 0)

        add_labor_sales = elr * tenths
        add_labor_gross = add_labor_sales * labor_margin
        add_parts_sales = add_labor_sales * parts_labor_ratio
        add_parts_gross = add_parts_sales * parts_margin
        total_add_gross_ro = add_labor_gross + add_parts_gross

        results = {
            "add_labor_sales_ro": add_labor_sales,
            "add_labor_gross_ro": add_labor_gross,
            "add_parts_sales_ro": add_parts_sales,
            "add_parts_gross_ro": add_parts_gross,
            "total_add_gross_ro": total_add_gross_ro,
            "monthly_impact": total_add_gross_ro * monthly_ros,
            "yearly_impact": total_add_gross_ro * monthly_ros * 12,
        }

    return render_template(
        "calculators/mpi.html",
        form=form,
        results=results,
        title="CP Menu and MPI Opportunity Calculator",
    )


@calculators_bp.route("/calculators/appointment", methods=["GET", "POST"])
@login_required
def appt_calculator():
    form = ApptCalculatorForm()

    if request.method == "GET":
        snapshot = get_current_month_snapshot(current_user.store_id)
        stats = snapshot["shop_stats"]

        form.num_techs.data = stats["tech_count"]
        form.proficiency.data = round(stats["proficiency"], 1)
        form.days_in_month.data = round(snapshot["total_workdays"], 1)
        form.avg_hours_per_ro.data = round(snapshot["avg_hours_per_ro"], 1)

        if hasattr(form, "show_rate") and not form.show_rate.data:
            form.show_rate.data = 90.0
        if hasattr(form, "walk_in_percent") and form.walk_in_percent.data in (None, ""):
            form.walk_in_percent.data = 10.0

    results = None
    if form.validate_on_submit():
        daily_capacity_hours = form.num_techs.data * 8 * (form.proficiency.data / 100.0)
        monthly_capacity_hours = daily_capacity_hours * form.days_in_month.data

        raw_daily_ro_goal = daily_capacity_hours / form.avg_hours_per_ro.data
        daily_ro_capacity = math.ceil(raw_daily_ro_goal)

        walk_in = form.walk_in_percent.data
        if walk_in > 1:
            walk_in = walk_in / 100.0

        show_rate = form.show_rate.data
        if show_rate > 1:
            show_rate = show_rate / 100.0

        appt_ros_needed = daily_ro_capacity * (1 - walk_in)
        daily_appt_goal = math.ceil(appt_ros_needed / show_rate)

        results = {
            "daily_capacity_hours": daily_capacity_hours,
            "monthly_capacity_hours": monthly_capacity_hours,
            "daily_ro_goal": daily_ro_capacity,
            "monthly_ro_goal": daily_ro_capacity * form.days_in_month.data,
            "daily_appt_goal": daily_appt_goal,
        }

    return render_template(
        "calculators/appointment.html",
        form=form,
        results=results,
        title="RO & Appointment Calculator",
    )


@calculators_bp.route("/calculators/cpgp", methods=["GET", "POST"])
@login_required
def cpgp_calculator():
    form = CPGPOpportunityForm()

    if request.method == "GET":
        snapshot = get_current_month_snapshot(current_user.store_id)
        stats = snapshot["shop_stats"]

        if snapshot["projected_month_end_cp_ros"] > 0:
            default_ro_count = int(round(snapshot["projected_month_end_cp_ros"]))
        elif snapshot["mtd_cp_ros"] > 0:
            default_ro_count = int(snapshot["mtd_cp_ros"])
        elif snapshot["ro_count_mtd"] > 0:
            default_ro_count = int(snapshot["ro_count_mtd"])
        else:
            default_ro_count = 0


        form.curr_elr.data = stats["elr"]
        form.curr_labor_margin.data = stats["labor_margin"]
        form.curr_parts_ratio.data = stats["parts_ratio"]
        form.curr_parts_margin.data = stats["parts_margin"]
        form.curr_hours_per_ro.data = round(snapshot["avg_hours_per_ro"], 1)
        form.curr_ro_count.data = default_ro_count

        form.opp_elr.data = stats["elr"]
        form.opp_labor_margin.data = stats["labor_margin"]
        form.opp_parts_ratio.data = stats["parts_ratio"]
        form.opp_parts_margin.data = stats["parts_margin"]
        form.opp_hours_per_ro.data = round(snapshot["avg_hours_per_ro"], 1)
        form.opp_ro_count.data = default_ro_count

        if form.curr_ro_count.data == 0 and stats["tech_count"] > 0:
            daily_cap_hours = stats["tech_count"] * 8 * (stats["proficiency"] / 100.0)
            monthly_cap_hours = daily_cap_hours * snapshot["total_workdays"]
            estimated_ros = int(monthly_cap_hours / max(snapshot["avg_hours_per_ro"], 1.0))
            form.curr_ro_count.data = estimated_ros
            form.opp_ro_count.data = estimated_ros

    results = None
    if form.validate_on_submit():

        def calc_metrics(elr, hours_per_ro, labor_margin, parts_ratio, parts_margin, ro_count):
            labor_sales = elr * hours_per_ro
            labor_gp = labor_sales * (labor_margin / 100.0)
            parts_sales = labor_sales * parts_ratio
            parts_gp = parts_sales * (parts_margin / 100.0)
            total_gp_ro = labor_gp + parts_gp
            total_monthly_gp = total_gp_ro * ro_count
            return total_gp_ro, total_monthly_gp

        curr_ro, curr_total = calc_metrics(
            form.curr_elr.data,
            form.curr_hours_per_ro.data,
            form.curr_labor_margin.data,
            form.curr_parts_ratio.data,
            form.curr_parts_margin.data,
            form.curr_ro_count.data,
        )

        opp_ro, opp_total = calc_metrics(
            form.opp_elr.data,
            form.opp_hours_per_ro.data,
            form.opp_labor_margin.data,
            form.opp_parts_ratio.data,
            form.opp_parts_margin.data,
            form.opp_ro_count.data,
        )

        results = {
            "current_gp_ro": curr_ro,
            "opportunity_gp_ro": opp_ro,
            "variance_ro": opp_ro - curr_ro,
            "current_monthly_gp": curr_total,
            "opportunity_monthly_gp": opp_total,
            "monthly_variance": opp_total - curr_total,
            "yearly_variance": (opp_total - curr_total) * 12,
        }

    return render_template(
        "calculators/cpgp.html",
        form=form,
        results=results,
        title="CP Gross Profit Opportunity",
    )


@calculators_bp.route("/calculators/capacity", methods=["GET", "POST"])
@login_required
def capacity_calculator():
    form = CapacityOpportunityForm()

    if request.method == "GET":
        snapshot = get_current_month_snapshot(current_user.store_id)
        stats = snapshot["shop_stats"]

        form.curr_tech_count.data = stats["tech_count"]
        form.curr_proficiency.data = round(stats["proficiency"], 1)
        form.curr_elr.data = stats["elr"]
        form.curr_labor_margin.data = stats["labor_margin"]
        form.curr_parts_ratio.data = stats["parts_ratio"]
        form.curr_parts_margin.data = stats["parts_margin"]
        form.curr_unapplied.data = int(stats["unapplied"])
        form.days_in_month.data = round(snapshot["total_workdays"], 1)

        form.opp_tech_count.data = stats["tech_count"]
        form.opp_proficiency.data = round(stats["proficiency"], 1)
        form.opp_elr.data = stats["elr"]
        form.opp_labor_margin.data = stats["labor_margin"]
        form.opp_parts_ratio.data = stats["parts_ratio"]
        form.opp_parts_margin.data = stats["parts_margin"]
        form.opp_unapplied.data = int(stats["unapplied"])

        if hasattr(form, "hours_per_day") and not form.hours_per_day.data:
            form.hours_per_day.data = 8.0

    results = None
    if form.validate_on_submit():

        def calc_forecast(
            techs,
            proficiency,
            days_in_month,
            hours_per_day,
            elr,
            labor_margin,
            parts_ratio,
            parts_margin,
            unapplied,
        ):
            total_hours = techs * hours_per_day * (proficiency / 100.0) * days_in_month
            labor_sales = total_hours * elr
            labor_gp = (labor_sales * (labor_margin / 100.0)) - abs(unapplied)
            parts_sales = labor_sales * parts_ratio
            parts_gp = parts_sales * (parts_margin / 100.0)
            return labor_gp, parts_gp, labor_gp + parts_gp

        curr_labor, curr_parts, curr_total = calc_forecast(
            form.curr_tech_count.data,
            form.curr_proficiency.data,
            form.days_in_month.data,
            form.hours_per_day.data,
            form.curr_elr.data,
            form.curr_labor_margin.data,
            form.curr_parts_ratio.data,
            form.curr_parts_margin.data,
            form.curr_unapplied.data,
        )

        opp_labor, opp_parts, opp_total = calc_forecast(
            form.opp_tech_count.data,
            form.opp_proficiency.data,
            form.days_in_month.data,
            form.hours_per_day.data,
            form.opp_elr.data,
            form.opp_labor_margin.data,
            form.opp_parts_ratio.data,
            form.opp_parts_margin.data,
            form.opp_unapplied.data,
        )

        results = {
            "current": {"labor": curr_labor, "parts": curr_parts, "total": curr_total},
            "opportunity": {"labor": opp_labor, "parts": opp_parts, "total": opp_total},
            "variance": opp_total - curr_total,
            "annualized": (opp_total - curr_total) * 12,
        }

    return render_template(
        "calculators/capacity.html",
        form=form,
        results=results,
        title="Service RO Opportunity Worksheet",
    )


@calculators_bp.route("/calculators/pace-recovery", methods=["GET", "POST"])
@login_required
def pace_recovery_calculator():
    form = PaceRecoveryCalculatorForm()

    if request.method == "GET":
        snapshot = get_current_month_snapshot(current_user.store_id)

        form.monthly_forecast_gross.data = round(snapshot["monthly_forecast_gross"], 0)
        form.mtd_actual_gross.data = round(snapshot["mtd_total_gross"], 0)
        form.monthly_frh_goal.data = round(snapshot["monthly_frh_goal"], 1)
        form.mtd_actual_frh.data = round(snapshot["mtd_actual_frh"], 1)
        form.elapsed_workdays.data = round(snapshot["elapsed_workdays"], 1)
        form.remaining_workdays.data = round(snapshot["remaining_workdays"], 1)
        form.avg_hours_per_ro.data = round(snapshot["avg_hours_per_ro"], 1)
        form.avg_gross_per_ro.data = round(snapshot["avg_gross_per_ro"], 0)

    results = None
    if form.validate_on_submit():
        monthly_forecast_gross = safe_float(form.monthly_forecast_gross.data)
        mtd_actual_gross = safe_float(form.mtd_actual_gross.data)
        monthly_frh_goal = safe_float(form.monthly_frh_goal.data)
        mtd_actual_frh = safe_float(form.mtd_actual_frh.data)
        elapsed_workdays = safe_float(form.elapsed_workdays.data)
        remaining_workdays = safe_float(form.remaining_workdays.data)
        avg_hours_per_ro = safe_float(form.avg_hours_per_ro.data)
        avg_gross_per_ro = safe_float(form.avg_gross_per_ro.data)

        total_workdays = elapsed_workdays + remaining_workdays

        expected_mtd_gross = (monthly_forecast_gross / total_workdays) * elapsed_workdays if total_workdays > 0 else 0.0
        expected_mtd_frh = (monthly_frh_goal / total_workdays) * elapsed_workdays if total_workdays > 0 else 0.0

        gross_gap = monthly_forecast_gross - mtd_actual_gross
        frh_gap = monthly_frh_goal - mtd_actual_frh

        daily_gross_add_on = gross_gap / remaining_workdays if remaining_workdays > 0 else 0.0
        daily_frh_add_on = frh_gap / remaining_workdays if remaining_workdays > 0 else 0.0

        extra_ros_per_day = daily_frh_add_on / avg_hours_per_ro if avg_hours_per_ro > 0 else 0.0
        extra_appts_per_day = daily_gross_add_on / avg_gross_per_ro if avg_gross_per_ro > 0 else 0.0

        projected_month_end_gross = (mtd_actual_gross / elapsed_workdays) * total_workdays if elapsed_workdays > 0 else 0.0
        projected_month_end_frh = (mtd_actual_frh / elapsed_workdays) * total_workdays if elapsed_workdays > 0 else 0.0

        results = {
            "expected_mtd_gross": expected_mtd_gross,
            "expected_mtd_frh": expected_mtd_frh,
            "gross_gap": gross_gap,
            "frh_gap": frh_gap,
            "daily_gross_add_on": daily_gross_add_on,
            "daily_frh_add_on": daily_frh_add_on,
            "extra_ros_per_day": extra_ros_per_day,
            "extra_appts_per_day": extra_appts_per_day,
            "projected_month_end_gross": projected_month_end_gross,
            "projected_month_end_frh": projected_month_end_frh,
        }

    return render_template(
        "calculators/pace_recovery.html",
        form=form,
        results=results,
        title="Pace Recovery Calculator",
    )


@calculators_bp.route("/calculators/appointment-lift", methods=["GET", "POST"])
@login_required
def appointment_lift_calculator():
    form = AppointmentLiftCalculatorForm()

    if request.method == "GET":
        snapshot = get_current_month_snapshot(current_user.store_id)

        form.additional_appointments.data = 5
        form.avg_hours_per_ro.data = round(snapshot["avg_hours_per_ro"], 1)
        form.avg_gross_per_ro.data = round(snapshot["avg_gross_per_ro"], 0)
        form.show_rate.data = 90.0
        form.workdays_per_month.data = round(snapshot["total_workdays"], 1)

    results = None
    if form.validate_on_submit():
        additional_appointments = int(form.additional_appointments.data or 0)
        avg_hours_per_ro = safe_float(form.avg_hours_per_ro.data)
        avg_gross_per_ro = safe_float(form.avg_gross_per_ro.data)
        show_rate = safe_float(form.show_rate.data) / 100.0
        workdays_per_month = safe_float(form.workdays_per_month.data)

        effective_shown_appointments = additional_appointments * show_rate
        added_frh_per_day = effective_shown_appointments * avg_hours_per_ro
        added_gross_per_day = effective_shown_appointments * avg_gross_per_ro

        monthly_added_frh = added_frh_per_day * workdays_per_month
        monthly_added_gross = added_gross_per_day * workdays_per_month

        results = {
            "effective_shown_appointments": effective_shown_appointments,
            "added_frh_per_day": added_frh_per_day,
            "added_gross_per_day": added_gross_per_day,
            "monthly_added_frh": monthly_added_frh,
            "monthly_added_gross": monthly_added_gross,
            "annual_added_gross": monthly_added_gross * 12,
        }

    return render_template(
        "calculators/appointment_lift.html",
        form=form,
        results=results,
        title="Appointment Lift Calculator",
    )
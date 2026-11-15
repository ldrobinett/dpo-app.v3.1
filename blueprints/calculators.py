
from flask import Blueprint, current_app, render_template, request, session
from flask_login import login_required, current_user
from sqlalchemy import func
from .management_intelligence import evaluate_pilot, manager_focus
from services.calculator_direction import CHECKS, calculator_direction
from services.local_focus import snapshot_key
from services.pace_recovery import recovery_estimate, recovery_next_step
from utils.permissions import has_capability

from extensions import db
from models import (
    DailyMetrics,
    FinancialForecast,
    FinancialInputs, StoreForecastInputs,
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
import sqlite3

calculators_bp = Blueprint("calculators", __name__)


@calculators_bp.context_processor
def calculator_management_guidance():
    endpoint = (request.endpoint or "").rsplit(".", 1)[-1]
    if endpoint not in CHECKS or not has_capability("manage.view"):
        return {}
    pilot = current_app.config.get("MI_LOCAL_PILOT")
    if (not pilot or current_user.is_operator or pilot["store_id"] != current_user.store_id
            or db.engine.url.get_backend_name() != "sqlite"):
        return {}
    try:
        case, result = evaluate_pilot(pilot)
    except (OSError, ValueError, sqlite3.Error):
        current_app.logger.exception("Could not evaluate Management Intelligence for the calculator")
        return {"calculator_guidance": dict(status="Store evidence unavailable", calculator=endpoint)}
    guidance = calculator_direction(endpoint, case, result)
    guidance["focus"] = manager_focus(case, result)
    return {"calculator_guidance": guidance}


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

    from services.forecast_inputs import as_inputs
    shared = db.session.get(StoreForecastInputs, store_id)
    inputs = as_inputs(shared) if shared else FinancialInputs.query.filter(FinancialInputs.user_id == current_user.id).first()
    if inputs:
        stats["elr"] = safe_float(inputs.effective_labor_rate)
        stats["labor_margin"] = safe_float(inputs.labor_margin)
        stats["parts_ratio"] = safe_float(inputs.parts_to_labor_ratio)
        stats["parts_margin"] = safe_float(inputs.parts_margin)
        stats["unapplied"] = safe_float(inputs.unapplied_time_cost)

    techs = (
        TeamMember.query.join(Team)
        .filter(
            Team.store_id == store_id,
            TeamMember.retired_at.is_(None),
        )
        .all()
    )
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


def customer_pay_assumptions(store_id, user_id):
    shared = db.session.get(StoreForecastInputs, store_id)
    inputs = FinancialInputs.query.filter_by(user_id=user_id).first()
    assumptions = {}
    for setting in ("effective_labor_rate", "labor_margin", "parts_to_labor_ratio", "parts_margin"):
        cp_value = getattr(inputs, f"cp_{setting}", None)
        default = shared.values.get(setting) if shared else getattr(inputs, setting, None)
        if cp_value is not None:
            assumptions[setting] = cp_value, "Saved customer-pay setting"
        elif default is not None:
            assumptions[setting] = default, "All-pay forecast input · confirm for customer-pay"

    reporting_date = get_reporting_date()
    start, end = get_month_boundaries(reporting_date)
    metrics = get_latest_daily_metrics(store_id, start, reporting_date)
    if metrics is not None and metrics.cp_ros_mtd is not None:
        elapsed = count_workdays(start, metrics.date)
        if elapsed:
            monthly_volume = round(metrics.cp_ros_mtd * count_workdays(start, end) / elapsed)
            assumptions["monthly_cp_ros"] = monthly_volume, f"Projected from CP ROs through {metrics.date:%b %d}"
    return assumptions


@calculators_bp.route("/calculators/mpi", methods=["GET", "POST"])
@login_required
def mpi_calculator():
    form = MPICalculatorForm()
    assumptions = customer_pay_assumptions(current_user.store_id, current_user.id)
    fields = {
        "monthly_cp_ros": "monthly_cp_ros", "tenths_increase": "tenths_increase",
        "effective_labor_rate": "effective_labor_rate", "labor_gross_margin": "labor_margin",
        "parts_to_labor_ratio": "parts_to_labor_ratio", "parts_gross_margin": "parts_margin",
    }
    assumptions["tenths_increase"] = 0.3, "Starting scenario"
    sources = {}
    for name, setting in fields.items():
        value, source = assumptions.get(setting, (None, "Needs entry"))
        field = form[name]
        if request.method == "GET":
            field.data = value
        sources[name] = source if field.data == value else "Entered for this scenario"

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
        if not all(math.isfinite(value) for value in results.values()):
            form.effective_labor_rate.errors.append("Check the amounts. The calculation is too large.")
            results = None

    return render_template(
        "calculators/mpi.html",
        form=form,
        results=results,
        sources=sources,
        title="Added Lines Calculator",
    )


@calculators_bp.route("/calculators/appointment", methods=["GET", "POST"])
@login_required
def appt_calculator():
    form = ApptCalculatorForm()

    snapshot = get_current_month_snapshot(current_user.store_id)
    assumptions = {
        "num_techs": (snapshot["shop_stats"]["tech_count"] or None, "Active roster · confirm daily availability"),
        "hours_per_tech": (8, "Starting assumption · enter working time after breaks"),
        "proficiency": (None, "Needs entry · confirm with the shop"),
        "days_in_month": (snapshot["total_workdays"], "Monday–Saturday · adjust for store closures"),
        "avg_hours_per_ro": (None, "Needs entry · confirm your job mix"),
        "walk_in_percent": (10, "Starting assumption"),
        "show_rate": (90, "Starting assumption"),
    }
    if snapshot["ro_count_mtd"] and snapshot["mtd_actual_frh"] > 0:
        assumptions["avg_hours_per_ro"] = (
            round(snapshot["mtd_actual_frh"] / snapshot["ro_count_mtd"], 2),
            f"All-pay Work Log through {snapshot['reporting_date']:%b %d}",
        )
    sources = {}
    for name, (value, source) in assumptions.items():
        field = form[name]
        if request.method == "GET":
            field.data = value
        sources[name] = source if field.data == value else "Entered for this scenario"

    results = None
    if form.validate_on_submit():
        daily_capacity_hours = form.num_techs.data * form.hours_per_tech.data * (form.proficiency.data / 100)
        monthly_capacity_hours = daily_capacity_hours * form.days_in_month.data
        raw_daily_ro_goal = daily_capacity_hours / form.avg_hours_per_ro.data
        if not all(math.isfinite(value) for value in (daily_capacity_hours, monthly_capacity_hours, raw_daily_ro_goal)):
            form.proficiency.errors.append("Check the assumptions. The calculation is too large.")
        else:
            daily_ro_goal = math.ceil(raw_daily_ro_goal)
            walk_in = form.walk_in_percent.data / 100
            show_rate = form.show_rate.data / 100
            appt_ros_needed = daily_ro_goal * (1 - walk_in)
            slots = appt_ros_needed / show_rate
            if math.isfinite(slots):
                results = {
                    "daily_capacity_hours": daily_capacity_hours,
                    "monthly_capacity_hours": monthly_capacity_hours,
                    "daily_ro_goal": daily_ro_goal,
                    "monthly_ro_goal": daily_ro_goal * form.days_in_month.data,
                    "daily_appt_goal": math.ceil(slots),
                    "appt_ros_needed": appt_ros_needed,
                }
            else:
                form.show_rate.errors.append("Check the show rate. The calculation is too large.")

    return render_template(
        "calculators/appointment.html",
        form=form,
        sources=sources,
        results=results,
        title="RO & Appointment Calculator",
    )


def customer_pay_gross(values):
    labor_sales = values["elr"] * values["hours_per_ro"]
    labor = labor_sales * (values["labor_margin"] / 100)
    parts = labor_sales * values["parts_ratio"] * (values["parts_margin"] / 100)
    volume = values["ro_count"]
    return dict(labor=labor * volume, parts=parts * volume, per_ro=labor + parts,
                monthly=(labor + parts) * volume)


@calculators_bp.route("/calculators/cpgp", methods=["GET", "POST"])
@login_required
def cpgp_calculator():
    form = CPGPOpportunityForm()
    drivers = (
        ("ro_count", "Monthly CP ROs", "ROs", "monthly_cp_ros"),
        ("hours_per_ro", "Sold hours per CP RO", "FRH", "hours_per_ro"),
        ("elr", "CP effective labor rate", "$ / FRH", "effective_labor_rate"),
        ("labor_margin", "Labor gross margin", "%", "labor_margin"),
        ("parts_ratio", "Parts sales per $1 of labor", "", "parts_to_labor_ratio"),
        ("parts_margin", "Parts gross margin", "%", "parts_margin"),
    )
    assumptions = customer_pay_assumptions(current_user.store_id, current_user.id)
    sources = {}
    for key, _, _, setting in drivers:
        value, source = assumptions.get(setting, (None, "Needs entry from the CP report"))
        current, target = form[f"curr_{key}"], form[f"opp_{key}"]
        if request.method == "GET":
            current.data = target.data = value
        sources[key] = source if current.data == value else "Entered for this scenario"

    results = None
    if form.validate_on_submit():
        current = {key: form[f"curr_{key}"].data for key, *_ in drivers}
        target = {key: form[f"opp_{key}"].data for key, *_ in drivers}
        baseline = customer_pay_gross(current)
        scenario = customer_pay_gross(target)
        difference = scenario["monthly"] - baseline["monthly"]
        annualized = difference * 12
        effects = []
        for key, label, unit, _ in drivers:
            if current[key] == target[key]:
                continue
            single = customer_pay_gross({**current, key: target[key]})
            effects.append(dict(label=label, unit=unit, current=current[key], target=target[key],
                                effect=single["monthly"] - baseline["monthly"]))
        if all(math.isfinite(amount) for amount in [
            *baseline.values(), *scenario.values(), difference, annualized, *(item["effect"] for item in effects),
        ]):
            results = dict(current=baseline, target=scenario, difference=difference, annualized=annualized,
                           effects=sorted(effects, key=lambda item: abs(item["effect"]), reverse=True))
        else:
            form.opp_ro_count.errors.append("Check the assumptions. The calculation is too large.")

    return render_template(
        "calculators/cpgp.html", form=form, results=results, sources=sources,
        drivers=drivers, title="CP Gross Profit Opportunity",
    )


def modeled_capacity(values):
    daily = values["tech_count"] * values["hours_per_day"] * (values["proficiency"] / 100)
    return dict(daily=daily, monthly=daily * values["days_in_month"])


def gross_at_capacity(hours, values):
    labor_sales = hours * values["elr"]
    labor = labor_sales * (values["labor_margin"] / 100) - abs(values["unapplied"])
    parts = labor_sales * values["parts_ratio"] * (values["parts_margin"] / 100)
    return dict(labor=labor, parts=parts, total=labor + parts)


@calculators_bp.route("/calculators/capacity", methods=["GET", "POST"])
@login_required
def capacity_calculator():
    form = CapacityOpportunityForm()
    capacity_fields = (
        ("tech_count", "curr_tech_count", "Techs available", "techs"),
        ("hours_per_day", "hours_per_day", "Working hours per tech", "hrs"),
        ("days_in_month", "days_in_month", "Shop days", "days"),
        ("proficiency", "curr_proficiency", "Proficiency", "%"),
    )
    financial_fields = (
        ("elr", "effective_labor_rate", "$ / FRH"),
        ("labor_margin", "labor_margin", "%"),
        ("parts_ratio", "parts_to_labor_ratio", ""),
        ("parts_margin", "parts_margin", "%"),
        ("unapplied", "unapplied_time_cost", "$"),
    )
    store_id = current_user.store_id
    tech_count = TeamMember.query.join(Team).filter(
        Team.store_id == store_id, TeamMember.retired_at.is_(None),
    ).count()
    start, end = get_month_boundaries(get_reporting_date())
    assumptions = {
        "tech_count": (tech_count or None, "Active roster · confirm daily availability"),
        "hours_per_day": (8, "Starting assumption · exclude breaks"),
        "days_in_month": (count_workdays(start, end), "Monday–Saturday · adjust for closures"),
        "proficiency": (None, "Needs entry from your shop"),
    }
    shared = db.session.get(StoreForecastInputs, store_id)
    user_inputs = FinancialInputs.query.filter_by(user_id=current_user.id).first()
    for key, setting, _ in financial_fields:
        if shared and shared.values.get(setting) is not None:
            assumptions[key] = shared.values[setting], "Saved store forecast input"
        elif not shared and getattr(user_inputs, setting, None) is not None:
            assumptions[key] = getattr(user_inputs, setting), "Saved finance input"

    field_pairs = [(key, current_name) for key, current_name, _, _ in capacity_fields]
    field_pairs += [(key, f"curr_{key}") for key, _, _ in financial_fields]
    sources = {}
    for key, current_name in field_pairs:
        value, source = assumptions.get(key, (None, "Optional · not entered"))
        current, target = form[current_name], form[f"opp_{key}"]
        if request.method == "GET":
            current.data = target.data = value
        sources[key] = source if current.data == value else "Entered for this scenario"

    results = None
    if form.validate_on_submit():
        current = {key: form[name].data for key, name, _, _ in capacity_fields}
        target = {key: form[f"opp_{key}"].data for key, *_ in capacity_fields}
        baseline, scenario = modeled_capacity(current), modeled_capacity(target)
        gap = scenario["monthly"] - baseline["monthly"]
        effects = []
        for key, _, label, unit in capacity_fields:
            if current[key] != target[key]:
                effect = modeled_capacity({**current, key: target[key]})["monthly"] - baseline["monthly"]
                effects.append(dict(label=label, unit=unit, current=current[key], target=target[key], effect=effect))
        if all(math.isfinite(value) for value in [
            *baseline.values(), *scenario.values(), gap, *(item["effect"] for item in effects),
        ]):
            results = dict(current=baseline, target=scenario, gap=gap,
                           effects=sorted(effects, key=lambda item: abs(item["effect"]), reverse=True))
            if form.demand_hours.data is not None:
                demand = form.demand_hours.data
                results["demand"] = dict(entered=demand, covered=min(scenario["monthly"], demand),
                                         uncovered=max(0, scenario["monthly"] - demand))
            economics = {
                side: {key: form[f"{prefix}_{key}"].data for key, *_ in financial_fields}
                for side, prefix in (("current", "curr"), ("target", "opp"))
            }
            if all(value is not None for values in economics.values() for value in values.values()):
                gross = {side: gross_at_capacity(results[side]["monthly"], values) for side, values in economics.items()}
                gross_gap = gross["target"]["total"] - gross["current"]["total"]
                if all(math.isfinite(value) for values in gross.values() for value in values.values()) and math.isfinite(gross_gap):
                    results["gross"] = dict(**gross, gap=gross_gap)
                else:
                    form.opp_elr.errors.append("Check the gross assumptions. The calculation is too large.")
        else:
            form.opp_proficiency.errors.append("Check the capacity assumptions. The calculation is too large.")

    return render_template(
        "calculators/capacity.html", title="Capacity Opportunity", form=form, results=results,
        capacity_fields=capacity_fields, financial_fields=financial_fields, sources=sources,
    )


@calculators_bp.route("/calculators/pace-recovery", methods=["GET", "POST"])
@login_required
def pace_recovery_calculator():
    form = PaceRecoveryCalculatorForm()
    snapshot = get_current_month_snapshot(current_user.store_id)
    report_date = snapshot["reporting_date"]
    forecast, metrics = snapshot["forecast"], snapshot["latest_metrics"]
    assumptions = {
        "monthly_frh_goal": (forecast.expected_frh if forecast else None, "Saved monthly forecast"),
        "mtd_actual_frh": (
            round(snapshot["mtd_actual_frh"], 2) if snapshot["ro_count_mtd"] else None,
            f"Work Log through {report_date:%b %d} · confirm coverage",
        ),
        "elapsed_workdays": (snapshot["elapsed_workdays"], "Monday–Saturday · adjust for closures"),
        "remaining_workdays": (
            snapshot["total_workdays"] - snapshot["elapsed_workdays"], "Monday–Saturday · adjust for closures",
        ),
        "monthly_forecast_gross": (forecast.total_gross if forecast else None, "Saved monthly forecast"),
        "mtd_actual_gross": (
            metrics.total_gross if metrics and metrics.date == report_date else None,
            f"MTD report through {report_date:%b %d}",
        ),
        "avg_hours_per_ro": (None, "Optional · use the mix of work you can add"),
        "avg_gross_per_ro": (None, "Optional · same work mix as hours per RO"),
        "extra_capacity_per_day": (None, "Additional time the shop can deliver above its current pace"),
        "extra_demand_per_day": (None, "Additional authorized or supported work above its current pace"),
    }
    sources = {}
    for name, (value, source) in assumptions.items():
        field = form[name]
        if request.method == "GET":
            field.data = value
        sources[name] = source if field.data == value else "Entered for this scenario"
        if field.data is None and value is None and name in (
            "monthly_frh_goal", "mtd_actual_frh", "monthly_forecast_gross", "mtd_actual_gross",
        ):
            sources[name] = "Needs entry from the store report"

    results = next_step = draft = None
    if form.validate_on_submit():
        values = {name: form[name].data for name in assumptions}
        if values["elapsed_workdays"] + values["remaining_workdays"] > 31:
            form.remaining_workdays.errors.append("Elapsed and remaining days must fit in the same month.")
        else:
            estimate = recovery_estimate(values)
            if all(value is None or math.isfinite(value) for value in estimate.values()):
                results, next_step = estimate, recovery_next_step(values, estimate)
                pilot = current_app.config.get("MI_LOCAL_PILOT")
                if pilot and pilot["store_id"] == current_user.store_id and has_capability("manage.view"):
                    scenario = dict(through=report_date.isoformat(), values=values, result=results, **next_step)
                    draft = snapshot_key(scenario)
                    session["pace_recovery_draft"] = dict(
                        key=draft, store_id=current_user.store_id, user_id=current_user.get_id(), scenario=scenario,
                    )
            else:
                form.monthly_frh_goal.errors.append("Check the amounts. The calculation is too large.")

    return render_template(
        "calculators/pace_recovery.html", form=form, results=results, sources=sources,
        title="Pace Recovery Calculator", next_step=next_step, draft=draft, report_date=report_date,
    )


@calculators_bp.route("/calculators/appointment-lift", methods=["GET", "POST"])
@login_required
def appointment_lift_calculator():
    form = AppointmentLiftCalculatorForm()
    snapshot = get_current_month_snapshot(current_user.store_id)
    report_date = snapshot["reporting_date"]
    if request.method == "GET":
        form.workdays_per_month.data = snapshot["total_workdays"]

    results = next_step = draft = None
    if form.validate_on_submit():
        names = ("additional_appointments", "show_rate", "spare_ros_per_day",
                 "avg_hours_per_ro", "avg_gross_per_ro", "workdays_per_month")
        values = {name: form[name].data for name in names}
        try:
            arrivals = values["additional_appointments"] * (values["show_rate"] / 100)
            capacity = values["spare_ros_per_day"]
            completed = min(arrivals, capacity) if capacity is not None else (0.0 if not arrivals else None)
            days = values["workdays_per_month"]
            hours, gross = values["avg_hours_per_ro"], values["avg_gross_per_ro"]
            estimate = dict(
                arrivals=arrivals, completed=completed,
                overflow=arrivals - completed if completed is not None else None,
                daily_hours=completed * hours if completed is not None else None,
                period_hours=completed * hours * days if completed is not None else None,
                period_gross=completed * gross * days if completed is not None and gross is not None else None,
            )
            if not all(value is None or math.isfinite(value) for value in estimate.values()):
                raise OverflowError
        except OverflowError:
            form.additional_appointments.errors.append("Check the amounts. The calculation is too large.")
        else:
            results = estimate
            if not arrivals:
                next_step = dict(
                    action="Check the booking plan and recent show rate before opening more slots.",
                    expected="Confirm whether the available demand can bring in additional work.",
                )
            elif not completed:
                next_step = dict(
                    action="Check technician and advisor coverage for the proposed slots.",
                    expected="Confirm how many extra ROs the shop can finish on time each day.",
                )
            else:
                next_step = dict(
                    action="Pilot extra bookings only in shifts with confirmed coverage and customer demand.",
                    expected=f"Over {days:g} workdays, check for {completed * days:,.1f} extra completed ROs "
                    f"and {estimate['period_hours']:,.1f} extra sold hours while keeping customer promises.",
                )
            pilot = current_app.config.get("MI_LOCAL_PILOT")
            if pilot and pilot["store_id"] == current_user.store_id and has_capability("manage.view"):
                scenario = dict(through=report_date.isoformat(), values=values, result=results, **next_step)
                draft = snapshot_key(scenario)
                session["appointment_lift_draft"] = dict(
                    key=draft, store_id=current_user.store_id, user_id=current_user.get_id(), scenario=scenario,
                )

    return render_template(
        "calculators/appointment_lift.html", form=form, results=results, next_step=next_step,
        draft=draft, title="Appointment Lift Calculator",
    )

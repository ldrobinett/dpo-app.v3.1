from flask import Blueprint, render_template, url_for, flash, redirect, request, current_app, abort
from flask_login import login_required, current_user, AnonymousUserMixin
from extensions import db
from models import (
    ScheduleEntry, WorkLog, TeamSchedule, Team,
    ProductionObjectiveMemo, FinancialForecast, FinancialInputs, StoreForecastInputs, TeamMember, User, ManagedStore
)
from forms import FinancialPerformanceForm
from services.forecast_inputs import (
    FIELDS, ForecastConflict, as_inputs, legacy_candidates, stage_inputs, values_from,
)
from datetime import date, time, timedelta, datetime
import calendar
import math
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from sqlalchemy.orm import joinedload
import traceback # Import for logging
from utils.permissions import has_capability, require_capability
from services.production_pace import shop_production_today
from .team_performance import build_progress, summarize_progress
from pytz import timezone

# Create the Blueprint
finance_bp = Blueprint('finance', __name__)

# --- HELPER FUNCTIONS ---

def safe_decimal_input(value):
    """Safely converts potential None/float/Decimal input to Decimal, defaults to 0."""
    if value is None:
        return Decimal('0.00')
    # Use str() conversion to preserve precision when converting float/DB values to Decimal.
    return Decimal(str(value))

def apply_financial_adjustments(forecast_data, user_inputs):
    """
    Applies the various user adjustments to the monthly base financial forecast.

    Logic applied:
    1. Labor Gross: Base Gross - Unapplied Time Cost + Other RO Gross (Service Revenue)
    2. Parts Gross: Base Gross + ALL Parts Adjustments (Retail, Wholesale, Inventory, Discounts)
    3. Other Gross: Set to 0.
    """
    from decimal import Decimal, InvalidOperation

    # Base Gross (from the daily forecast calculation)
    base_labor_gross = forecast_data.get('labor_gross', Decimal('0.00'))
    base_parts_gross = forecast_data.get('parts_gross', Decimal('0.00'))

    # --- Extract Adjustment Inputs using robust conversion ---

    # Service/Labor Adjustment
    other_ro_gross = safe_decimal_input(user_inputs.other_ro_gross)
    unapplied_time_cost = safe_decimal_input(user_inputs.unapplied_time_cost)

    # Parts Adjustments
    wholesale_gross = safe_decimal_input(user_inputs.wholesale_gross)
    parts_retail_gross = safe_decimal_input(user_inputs.parts_retail_gross)
    parts_inventory_adjust = safe_decimal_input(user_inputs.parts_inventory_adjust)
    parts_allowance = safe_decimal_input(user_inputs.parts_allowance)
    purchase_discounts = safe_decimal_input(user_inputs.purchase_discounts)

    # -------------------------------------------------------------
    # --- 1. Calculate FINAL Adjusted Gross Totals for each category ---
    # -------------------------------------------------------------

    # 1. FINAL LABOR GROSS TOTAL (Base + Other RO Gross - Unapplied Time Cost)
    final_labor_gross = (
        base_labor_gross
        + other_ro_gross               # ADDING Other RO Gross (Service Revenue)
        - abs(unapplied_time_cost)     # SUBTRACTING Unapplied Time Cost
    )

    # 2. FINAL PARTS GROSS TOTAL (Base + ALL Parts Adjustments)
    parts_adjustments = (
        wholesale_gross +
        parts_retail_gross +
        parts_inventory_adjust +
        parts_allowance +
        purchase_discounts
    )
    final_parts_gross = base_parts_gross + parts_adjustments

    # 3. FINAL OTHER GROSS TOTAL
    # Set to zero as adjustments are mapped to Labor or Parts Gross
    final_other_gross = Decimal('0.00')

    # 4. FINAL TOTAL GROSS
    final_total_gross = (
        final_labor_gross +
        final_parts_gross +
        final_other_gross
    )

    # --- Update and Return the Dictionary ---
    forecast_data.update({
        'labor_gross': final_labor_gross,
        'parts_gross': final_parts_gross,
        'other_gross': final_other_gross,
        'total_gross': final_total_gross,
    })

    return forecast_data


# --- ROUTES ---

@finance_bp.route("/dashboard", methods=['GET', 'POST'])
@login_required
@require_capability("finance.view")
def dashboard():
    default_forecast = {
    'labor_gross': Decimal('0.00'), 'parts_gross': Decimal('0.00'),
    'other_gross': Decimal('0.00'), 'total_gross': Decimal('0.00'),
    'expected_frh': Decimal('0.00'),
    }

    def safe_decimal(value):
        if value is None: return Decimal(0)
        return Decimal(str(value))

    # --- Initialization ---
    financial_data = defaultdict(lambda: default_forecast.copy())
    weekly_financial_total = default_forecast.copy()
    next_weekly_financial_total = default_forecast.copy()
    full_month_financial_forecast = default_forecast.copy()
    weekly_member_data = {}

    # --- Robust User Check ---
    if not current_user.is_authenticated or isinstance(current_user._get_current_object(), AnonymousUserMixin):
        flash('Session expired or user not fully authenticated. Please log in.', 'warning')
        return redirect(url_for('auth.login'))

    store_id = current_user.store_id

    shared_inputs = db.session.get(StoreForecastInputs, store_id)
    candidates = legacy_candidates(store_id) if not shared_inputs else []
    user_inputs = as_inputs(shared_inputs)
    # Legacy values are preview-only until an explicit reviewed Save.
    selected_source = request.args.get('source', type=int)
    if not shared_inputs:
        selected = next((row for row, _ in candidates if row.user_id == selected_source), None)
        if selected is None and len(candidates) == 1:
            selected = candidates[0][0]
        user_inputs = selected

    financial_form = FinancialPerformanceForm(obj=user_inputs)
    if request.method == 'GET' and user_inputs:
        # Form field name differs from the database attribute.
        financial_form.elr.data = user_inputs.effective_labor_rate

    saving = False
    if request.method == 'POST':
        financial_form = FinancialPerformanceForm(request.form)
        for field in FIELDS:
            raw = request.form.get('elr' if field == 'effective_labor_rate' else field, '')
            if raw.strip():
                try:
                    if not Decimal(raw).is_finite():
                        return 'Financial inputs must be finite numbers. Nothing was saved.', 400
                except InvalidOperation:
                    pass  # Standard form validation will explain nonnumeric input.
        if financial_form.validate_on_submit():
            expected_version = request.form.get('input_version', type=int)
            if expected_version is None or expected_version < 0:
                return 'Missing input version. Reload the forecast before saving.', 409
            if expected_version == 0 and request.form.get('confirm_shared_inputs') != 'yes':
                return 'Review the legacy inputs and confirm the shared values before saving.', 409
            values = {field: (float(financial_form[field if field != 'effective_labor_rate' else 'elr'].data)
                              if financial_form[field if field != 'effective_labor_rate' else 'elr'].data is not None else None)
                      for field in FIELDS}
            if any(value is not None and not math.isfinite(value) for value in values.values()):
                return 'Financial inputs must be finite numbers. Nothing was saved.', 400
            try:
                user_inputs = stage_inputs(store_id, current_user.id, expected_version, values)
            except ForecastConflict as exc:
                return str(exc), 409
            saving = True
        else:
            flash('Inputs were not saved. Please correct the form errors.', 'danger')

    # --- GET Request & Calculations ---

    # Timeframes
    today = date.today()
    start_of_month = today.replace(day=1)
    _, days_in_month = calendar.monthrange(today.year, today.month)
    end_of_month = today.replace(day=days_in_month)
    current_month_name = today.strftime('%B')
    current_year = today.year

    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    start_of_next_week = start_of_week + timedelta(days=7)
    end_of_next_week = start_of_next_week + timedelta(days=6)

    # [FILTER] Filter schedules by store_id
    all_schedules_in_range = ScheduleEntry.query.join(TeamMember).join(Team).filter(
        Team.store_id == store_id,
        ScheduleEntry.date >= start_of_month,
        ScheduleEntry.date <= end_of_month # Pull for the ENTIRE MONTH
    ).options(joinedload(ScheduleEntry.team_member)).all()

    financial_data = defaultdict(lambda: default_forecast.copy())

    # This loop populates 'expected_frh' for all days
    for s in all_schedules_in_range:

        # --- NEW CHECK: ONLY count if schedule_type is WORK ---
        if s.schedule_type != 'WORK':
            continue # Skip this entry if it's PTO, TRAINING, or HOLIDAY
        # --- END NEW CHECK ---

        member = s.team_member
        if member and member.daily_production_objective is not None:

            # --- FRH CALC FIX: Use calculated DPO if mode is set ---
            frh_value = member.daily_production_objective
            if getattr(member, 'dpo_calculation_mode', 'manual') == 'calculated':
                frh_value = member.calculated_dpo

            expected_frh_day = safe_decimal(frh_value)
            financial_data[s.date]['expected_frh'] += expected_frh_day

    # Now, if inputs exist, calculate the financial values (Phase 1)
    if user_inputs:
        elr = safe_decimal(user_inputs.effective_labor_rate)
        parts_to_labor_ratio = safe_decimal(user_inputs.parts_to_labor_ratio)
        labor_margin_rate = safe_decimal(user_inputs.labor_margin) / Decimal(100)
        parts_margin_rate = safe_decimal(user_inputs.parts_margin) / Decimal(100)

        # Re-populate financial_data with gross values (Phase 1)
        for d, data in financial_data.items():
            if data['expected_frh'] > 0:
                expected_frh_day = data['expected_frh']

                # Calculate REVENUE first
                labor_revenue = expected_frh_day * elr
                parts_revenue = labor_revenue * parts_to_labor_ratio

                # Calculate GROSS PROFIT (Revenue * Margin %)
                labor_gross = labor_revenue * labor_margin_rate
                parts_gross = parts_revenue * parts_margin_rate

                total_gross = labor_gross + parts_gross

                financial_data[d]['labor_gross'] = labor_gross
                financial_data[d]['parts_gross'] = parts_gross
                financial_data[d]['total_gross'] = total_gross

    # Calculate Weekly Totals & MTD Expected FRH
    weekly_financial_total = default_forecast.copy()
    next_weekly_financial_total = default_forecast.copy()
    expected_frh_mtd_decimal = Decimal('0.00')

    for d, data in financial_data.items():
        if start_of_week <= d <= end_of_week:
            for k, v in data.items(): weekly_financial_total[k] += v
        if start_of_next_week <= d <= end_of_next_week:
            for k, v in data.items(): next_weekly_financial_total[k] += v
        if start_of_month <= d <= today:
            expected_frh_mtd_decimal += data['expected_frh']

    # Calculate Full Month Forecast (Base)
    base_month_total = default_forecast.copy()
    for d, data in financial_data.items():
        if start_of_month <= d <= end_of_month:
            for k, v in data.items(): base_month_total[k] += v

    # Apply adjustments if inputs exist (Phase 2)
    if user_inputs:
        full_month_financial_forecast = apply_financial_adjustments(base_month_total.copy(), user_inputs)
        full_month_financial_forecast['expected_frh'] = base_month_total['expected_frh']
    else:
        full_month_financial_forecast = base_month_total

    # Save the forecast
    if saving:
        forecast_entry = FinancialForecast.query.filter_by(
            month=today.month,
            year=today.year,
            store_id=store_id
        ).first()

        if not forecast_entry:
            forecast_entry = FinancialForecast(
                month=today.month,
                year=today.year,
                store_id=store_id
            )
            db.session.add(forecast_entry)

        forecast_entry.labor_gross = full_month_financial_forecast['labor_gross']
        forecast_entry.parts_gross = full_month_financial_forecast['parts_gross']
        forecast_entry.other_gross = full_month_financial_forecast['other_gross']
        forecast_entry.total_gross = full_month_financial_forecast['total_gross']
        forecast_entry.expected_frh = full_month_financial_forecast['expected_frh']
        forecast_entry.date_updated = date.today()

        db.session.commit()
        flash('Shared store inputs and monthly forecast saved successfully!', 'success')
        return redirect(url_for('finance.dashboard'))

    # --- MTD Member Data (Includes Avg Hrs/RO) ---
    all_members = TeamMember.query.join(Team).filter(Team.store_id == store_id).all()
    members_dict = {member.id: member for member in all_members}

    mtd_member_data = defaultdict(lambda: {
        'expected': 0.0, 'actual': 0.0, 'dpo': 0.0, 'ros': set()
    })

    for member in all_members:
        # --- FRH Calculation Logic: Use calculated DPO if mode is set ---
        frh_value = member.daily_production_objective
        if getattr(member, 'dpo_calculation_mode', 'manual') == 'calculated':
            frh_value = member.calculated_dpo

        mtd_member_data[member.id]['dpo'] = float(frh_value or 0.0)
        # --- End FRH Calculation Logic ---


    # Use the MTD value calculated earlier
    total_mtd_expected_frh = float(expected_frh_mtd_decimal)

    # Re-calculate per-tech expected MTD
    mtd_schedules = [s for s in all_schedules_in_range if start_of_month <= s.date <= today]
    for s in mtd_schedules:

        # --- NEW CHECK: ONLY count if schedule_type is WORK ---
        if s.schedule_type != 'WORK':
            continue # Skip non-productive days
        # --- END NEW CHECK ---

        if s.team_member:
            member = s.team_member

            # --- FRH Calculation Logic: Use calculated DPO if mode is set ---
            frh_value = member.daily_production_objective
            if getattr(member, 'dpo_calculation_mode', 'manual') == 'calculated':
                frh_value = member.calculated_dpo

            dpo_value = float(frh_value or 0.0)
            # --- End FRH Calculation Logic ---

            if dpo_value > 0:
                mtd_member_data[s.team_member_id]['expected'] += dpo_value

    # Calculate MTD Actual FRH & Track ROs
    mtd_logs = WorkLog.query.join(TeamMember).join(Team).filter(
        Team.store_id == store_id,
        WorkLog.date >= start_of_month,
        WorkLog.date <= today
    ).all()

    total_mtd_actual_frh = 0.0
    all_shop_ros = set()

    for log in mtd_logs:
        if log.team_member_id and log.flat_rate_hours and log.ro_number and log.ro_number.strip():
            member_id = log.team_member_id
            frh = float(log.flat_rate_hours)
            ro_num = log.ro_number.strip()

            if member_id in mtd_member_data:
                mtd_member_data[member_id]['actual'] += frh
                mtd_member_data[member_id]['ros'].add(ro_num)

            total_mtd_actual_frh += frh
            all_shop_ros.add(ro_num)

    # Calculate Averages
    shop_avg_hrs_per_ro = 0.0
    if all_shop_ros:
        shop_avg_hrs_per_ro = total_mtd_actual_frh / len(all_shop_ros)

    for member_id in mtd_member_data:
        ro_count = len(mtd_member_data[member_id]['ros'])
        mtd_member_data[member_id]['avg_hrs_per_ro'] = (mtd_member_data[member_id]['actual'] / ro_count) if ro_count > 0 else 0.0

    return render_template('dashboard.html',
                           title='Dashboard',
                           weekly_member_data=weekly_member_data,
                           mtd_member_data=mtd_member_data,
                           financial_form=financial_form,
                           input_version=(request.form.get('input_version', '') if request.method == 'POST' else (shared_inputs.version if shared_inputs else 0)),
                           legacy_candidates=candidates,
                           input_fields=FIELDS,
                           shared_inputs=shared_inputs,
                           expected_frh_mtd=total_mtd_expected_frh, # Use MTD total
                           # [NEW] Pass Full Month Expected FRH
                           full_month_expected_frh=float(full_month_financial_forecast['expected_frh']),
                           total_mtd_actual_frh=total_mtd_actual_frh,
                           shop_avg_hrs_per_ro=shop_avg_hrs_per_ro,
                           financial_data=financial_data,
                           weekly_financial_total=weekly_financial_total,
                           next_weekly_financial_total=next_weekly_financial_total,
                           full_month_financial_forecast=full_month_financial_forecast,
                           current_week_dates=f"{start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d')}",
                           next_week_dates=f"{start_of_next_week.strftime('%b %d')} - {end_of_next_week.strftime('%b %d')}",
                           team_members=members_dict,
                           # [NEW] Add month/year
                           current_month_name=current_month_name,
                           current_year=current_year)


@finance_bp.route("/monthly_forecast")
@login_required
@require_capability("finance.view")
def monthly_forecast():
    # --- Robust User Check ---
    if not current_user.is_authenticated or isinstance(current_user._get_current_object(), AnonymousUserMixin):
        flash('Session expired or user not fully authenticated. Please log in.', 'warning')
        return redirect(url_for('auth.login'))

    all_forecasts = FinancialForecast.query.filter_by(
        store_id=current_user.store_id
    ).order_by(FinancialForecast.year.desc(), FinancialForecast.month.desc()).all()

    return render_template('monthly_forecast.html',
                           title='Monthly Forecast',
                           all_forecasts=all_forecasts)

@finance_bp.route("/production_display")
@login_required
def production_display():
    store_id = current_user.store_id
    if not store_id or not (has_capability("production.view") or has_capability("finance.view")):
        abort(403)

    now = datetime.now(timezone("America/Los_Angeles"))
    store = db.session.get(ManagedStore, store_id)
    if store is None:
        abort(404)
    today = now.date()
    month_start = today.replace(day=1)
    members = TeamMember.query.join(Team).options(joinedload(TeamMember.team)).filter(
        Team.store_id == store_id,
    ).order_by(Team.name, Team.id, TeamMember.name).all()
    logs = WorkLog.query.join(TeamMember).join(Team).filter(
        Team.store_id == store_id, WorkLog.date.between(month_start, today),
    ).all()
    shifts = ScheduleEntry.query.options(joinedload(ScheduleEntry.team_member)).join(TeamMember).join(Team).filter(
        Team.store_id == store_id, ScheduleEntry.date.between(month_start, today), ScheduleEntry.schedule_type == "WORK",
    ).all()
    pilot = current_app.config.get("MI_LOCAL_PILOT")
    pilot = pilot if pilot and pilot["store_id"] == store_id else None
    board = shop_production_today(
        now, [shift for shift in shifts if shift.date == today],
        [log for log in logs if log.date == today], targets_verified=pilot is None,
    )
    rows, _ = build_progress(members, shifts, logs, today)
    by_technician = {row["id"]: row for row in rows}
    team_production = {}
    for member in members:
        row = by_technician.get(member.id)
        if row:
            row["retired"] = bool(member.retired_at and member.retired_at.date() <= today)
            team_production.setdefault(member.team_id, {"name": member.team.name, "rows": []})["rows"].append(row)
    team_screens = []
    for team in team_production.values():
        rows = team["rows"]
        totals = {period: summarize_progress(rows, period) for period in ("today", "month")}
        page_size = 8
        page_count = (len(rows) + page_size - 1) // page_size
        for start in range(0, len(rows), page_size):
            team_screens.append(dict(
                name=team["name"], rows=rows[start:start + page_size], totals=totals,
                page=start // page_size + 1, pages=page_count,
            ))
    return render_template(
        "production_display.html", title="Live Production Display",
        store=store, now=now, board=board, pilot=pilot, team_screens=team_screens,
    )

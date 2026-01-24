from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_required, current_user, AnonymousUserMixin 
from extensions import db
from models import (
    ScheduleEntry, WorkLog, TeamSchedule, Team,
    ProductionObjectiveMemo, FinancialForecast, FinancialInputs, TeamMember, User
)
from forms import FinancialPerformanceForm
from datetime import date, time, timedelta, datetime
import calendar
from collections import defaultdict
from decimal import Decimal
from sqlalchemy.orm import joinedload
import traceback # Import for logging

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
    from decimal import Decimal

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


def get_production_display_data(store_id):
    """Calculates Today's and MTD performance data for each tech."""
    
    today = date.today()
    start_of_month = today.replace(day=1)
    
    member_data = defaultdict(lambda: {
        'name': 'Unknown', 'dpo': 0.0, 'actual_today': 0.0,
        'is_scheduled_today': False, 'expected_mtd': 0.0, 'actual_mtd': 0.0,
        'team_name': 'Unassigned'
    })

    # --- 1. Get all members and their basic info ---
    all_members = TeamMember.query.join(Team).filter(Team.store_id == store_id).options(joinedload(TeamMember.team)).order_by(TeamMember.name).all()
    for member in all_members:
        member_data[member.id]['name'] = member.name
        
        # --- FRH Calculation Logic: Use calculated DPO if mode is set ---
        frh_value = member.daily_production_objective
        if getattr(member, 'dpo_calculation_mode', 'manual') == 'calculated':
            frh_value = member.calculated_dpo
            
        member_data[member.id]['dpo'] = float(frh_value or 0.0) # Use the correct DPO
        # --- End FRH Calculation Logic ---
        
        member_data[member.id]['team_name'] = member.team.name if member.team else 'Unassigned'

    # --- 2. Calculate Today's Actuals (from WorkLogs) ---
    logs_today = WorkLog.query.join(TeamMember).join(Team).filter(
        Team.store_id == store_id,
        WorkLog.date == today
    ).all()
    
    for log in logs_today:
        if log.team_member_id and log.flat_rate_hours:
            member_data[log.team_member_id]['actual_today'] += float(log.flat_rate_hours)

    # --- 3. Check if Scheduled Today & Calculate MTD Expected (from Schedules) ---
    schedules_mtd = ScheduleEntry.query.join(TeamMember).join(Team).filter(
        Team.store_id == store_id,
        ScheduleEntry.date >= start_of_month,
        ScheduleEntry.date <= today
    ).options(
        joinedload(ScheduleEntry.team_member) # Only need member
    ).all()

    for s in schedules_mtd:
        
        # --- NEW CHECK: Skip non-productive entries ---
        if s.schedule_type != 'WORK':
            continue
        # --- END NEW CHECK ---
        
        if s.team_member:
            
            # --- FRH Calculation Logic: Use calculated DPO if mode is set ---
            member = s.team_member
            frh_value = member.daily_production_objective
            if getattr(member, 'dpo_calculation_mode', 'manual') == 'calculated':
                frh_value = member.calculated_dpo
                
            dpo = float(frh_value or 0.0) # Use the correct DPO
            # --- End FRH Calculation Logic ---
            
            if dpo > 0:
                member_id = s.team_member_id
                
                # Add to MTD expected total
                member_data[member_id]['expected_mtd'] += dpo
                
                # Check if scheduled today
                if s.date == today:
                    member_data[member_id]['is_scheduled_today'] = True

    # --- 4. Calculate MTD Actuals (from WorkLogs) ---
    logs_mtd = WorkLog.query.join(TeamMember).join(Team).filter(
        Team.store_id == store_id,
        WorkLog.date >= start_of_month,
        WorkLog.date <= today
    ).all()
    
    for log in logs_mtd:
        if log.team_member_id and log.flat_rate_hours:
            member_data[log.team_member_id]['actual_mtd'] += float(log.flat_rate_hours)

    # --- 5. Calculate Percentages and Final Formatting ---
    final_data_by_team = defaultdict(list)
    
    for member_id, data in member_data.items():
        dpo = data['dpo']
        actual_today = data['actual_today']
        is_scheduled_today = data['is_scheduled_today']
        expected_mtd = data['expected_mtd']
        actual_mtd = data['actual_mtd']
        
        percent_today = 0.0
        if is_scheduled_today and dpo > 0:
            percent_today = (actual_today / dpo) * 100
            
        percent_mtd = (actual_mtd / expected_mtd) * 100 if expected_mtd > 0 else 0
        
        data['percent_today'] = percent_today
        data['percent_mtd'] = percent_mtd
        
        if dpo > 0 or expected_mtd > 0 or actual_mtd > 0:
              final_data_by_team[data['team_name']].append(data)
              
    sorted_team_data = dict(sorted(final_data_by_team.items()))

    return sorted_team_data

# --- ROUTES ---

@finance_bp.route("/dashboard", methods=['GET', 'POST'])
@login_required
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
    
    # Query FinancialInputs solely by the user_id (Final robust retrieval)
    user_inputs = FinancialInputs.query.filter(
        FinancialInputs.user_id == current_user.id
    ).first()
    
    if user_inputs:
        financial_form = FinancialPerformanceForm(obj=user_inputs)
    else:
        financial_form = FinancialPerformanceForm()
    
    # --- POST Request ---
    if request.method == 'POST':
        financial_form = FinancialPerformanceForm(request.form)
        if financial_form.validate_on_submit():
            if not user_inputs:
                # Create new entry if none exists
                user_inputs = FinancialInputs(user_id=current_user.id)
                db.session.add(user_inputs)
            
            # Explicitly map ALL fields from form to model (Fixes saving issue)
            user_inputs.effective_labor_rate = financial_form.elr.data
            user_inputs.parts_to_labor_ratio = financial_form.parts_to_labor_ratio.data
            user_inputs.labor_margin = financial_form.labor_margin.data
            user_inputs.parts_margin = financial_form.parts_margin.data
            user_inputs.other_ro_gross = financial_form.other_ro_gross.data
            user_inputs.unapplied_time_cost = financial_form.unapplied_time_cost.data
            user_inputs.wholesale_gross = financial_form.wholesale_gross.data
            user_inputs.parts_retail_gross = financial_form.parts_retail_gross.data
            user_inputs.parts_inventory_adjust = financial_form.parts_inventory_adjust.data
            user_inputs.parts_allowance = financial_form.parts_allowance.data
            user_inputs.purchase_discounts = financial_form.purchase_discounts.data

            db.session.commit()
            flash('Financial inputs updated successfully!', 'success')
            return redirect(url_for('finance.dashboard'))
    # --- END POST Request ---

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
    if base_month_total['expected_frh'] > 0 or base_month_total['total_gross'] > 0:
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
    
    # Re-populate form if needed
    if user_inputs:
        financial_form = FinancialPerformanceForm(obj=user_inputs)
        financial_form.elr.data = user_inputs.effective_labor_rate
        
    return render_template('dashboard.html',
                           title='Dashboard',
                           weekly_member_data=weekly_member_data, 
                           mtd_member_data=mtd_member_data, 
                           financial_form=financial_form,
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

# === Production Display Route ===
@finance_bp.route("/production_display")
@login_required
def production_display():
    # --- Robust User Check ---
    if not current_user.is_authenticated or isinstance(current_user._get_current_object(), AnonymousUserMixin):
        flash('Session expired or user not fully authenticated. Please log in.', 'warning')
        return redirect(url_for('auth.login')) 
    
    production_data = get_production_display_data(current_user.store_id) 
    today_date_str = date.today().strftime("%A, %B %d, %Y")

    return render_template('production_display.html',
                           title="Live Production Display",
                           production_data=production_data,
                           today_date_str=today_date_str)

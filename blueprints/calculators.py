from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from extensions import db
from models import FinancialInputs, TeamMember, Team, TeamSchedule, ScheduleEntry
from forms import MPICalculatorForm, ApptCalculatorForm, CPGPOpportunityForm, CapacityOpportunityForm
from datetime import date, datetime, timedelta
import math 
import calendar

calculators_bp = Blueprint('calculators', __name__)

def get_shop_stats(store_id):
    """
    Helper to fetch current shop metrics.
    SCALES PERCENTAGES TO WHOLE NUMBERS (e.g. 0.75 -> 75.0) for display.
    CALCULATES AVG WORK DAYS based on ScheduleEntry.
    """
    stats = {
        'tech_count': 0,
        'proficiency': 0.0,
        'elr': 0.0,
        'labor_margin': 0.0,
        'parts_ratio': 0.0,
        'parts_margin': 0.0,
        'unapplied': 0.0,
        'work_days': 21.0 # Default
    }

    # 1. Financial Inputs
    inputs = FinancialInputs.query.filter(FinancialInputs.user_id == current_user.id).first()
    if inputs:
        def safe_val(v): return float(v) if v else 0.0
        stats['elr'] = safe_val(inputs.effective_labor_rate)
        stats['labor_margin'] = safe_val(inputs.labor_margin) 
        stats['parts_ratio'] = safe_val(inputs.parts_to_labor_ratio)
        stats['parts_margin'] = safe_val(inputs.parts_margin)
        stats['unapplied'] = safe_val(inputs.unapplied_time_cost)

    # 2. Tech Count & Proficiency
    techs = TeamMember.query.join(Team).filter(Team.store_id == store_id).all()
    stats['tech_count'] = len(techs)

    if techs:
        total_dpo = sum(float(t.daily_production_objective or 0) for t in techs)
        total_scheduled_hours = 0.0
        
        for tech in techs:
            daily_hrs = 8.0 
            if tech.team:
                schedules = TeamSchedule.query.filter_by(team_id=tech.team.id).all()
                if schedules:
                    weekly_hours = 0.0
                    for s in schedules:
                        start_dt = datetime.combine(date.min, s.start_time)
                        end_dt = datetime.combine(date.min, s.end_time)
                        duration = (end_dt - start_dt).total_seconds() / 3600
                        if s.lunch_start and s.lunch_end:
                            l_start = datetime.combine(date.min, s.lunch_start)
                            l_end = datetime.combine(date.min, s.lunch_end)
                            lunch = (l_end - l_start).total_seconds() / 3600
                            duration -= lunch
                        weekly_hours += duration
                    daily_hrs = weekly_hours / 5.0 if weekly_hours > 0 else 8.0
            total_scheduled_hours += daily_hrs
            
        if total_scheduled_hours > 0:
            stats['proficiency'] = (total_dpo / total_scheduled_hours) * 100.0

    # 3. Calculate Average Work Days in Current Month
    today = date.today()
    start_date = date(today.year, today.month, 1)
    last_day = calendar.monthrange(today.year, today.month)[1]
    end_date = date(today.year, today.month, last_day)

    total_scheduled_days = ScheduleEntry.query.join(TeamMember).join(Team).filter(
        Team.store_id == store_id,
        ScheduleEntry.date >= start_date,
        ScheduleEntry.date <= end_date,
        ScheduleEntry.schedule_type == 'WORK'
    ).count()

    if stats['tech_count'] > 0:
        avg_days = total_scheduled_days / stats['tech_count']
        if avg_days > 0:
            stats['work_days'] = avg_days

    return stats

@calculators_bp.route('/calculators/mpi', methods=['GET', 'POST'])
@login_required
def mpi_calculator():
    form = MPICalculatorForm()
    
    if request.method == 'GET':
        stats = get_shop_stats(current_user.store_id)
        form.effective_labor_rate.data = stats['elr']
        form.labor_gross_margin.data = stats['labor_margin']
        form.parts_to_labor_ratio.data = stats['parts_ratio']
        form.parts_gross_margin.data = stats['parts_margin']
        
        # Pre-fill Monthly RO Count based on Shop Capacity
        if stats['tech_count'] > 0:
            daily_cap_hours = stats['tech_count'] * 8 * (stats['proficiency'] / 100.0)
            monthly_cap_hours = daily_cap_hours * stats['work_days']
            estimated_ros = monthly_cap_hours / 2.0 
            form.monthly_cp_ros.data = int(estimated_ros)
        else:
            form.monthly_cp_ros.data = 0

    results = None
    if form.validate_on_submit():
        elr = form.effective_labor_rate.data
        tenths = form.tenths_increase.data
        l_margin = form.labor_gross_margin.data / 100.0
        pl_ratio = form.parts_to_labor_ratio.data
        p_margin = form.parts_gross_margin.data / 100.0
        monthly_ros = form.monthly_cp_ros.data
        
        add_labor_sales = elr * tenths
        add_labor_gross = add_labor_sales * l_margin
        add_parts_sales = add_labor_sales * pl_ratio
        add_parts_gross = add_parts_sales * p_margin
        total_add_gross_ro = add_labor_gross + add_parts_gross
        
        results = {
            'add_labor_sales_ro': add_labor_sales,
            'add_labor_gross_ro': add_labor_gross,
            'add_parts_sales_ro': add_parts_sales,
            'add_parts_gross_ro': add_parts_gross,
            'total_add_gross_ro': total_add_gross_ro,
            'monthly_impact': total_add_gross_ro * monthly_ros,
            'yearly_impact': total_add_gross_ro * monthly_ros * 12
        }
        
    return render_template('calculators/mpi.html', form=form, results=results, title="CP Menu and MPI Opportunity Calculator")

@calculators_bp.route('/calculators/appointment', methods=['GET', 'POST'])
@login_required
def appt_calculator():
    form = ApptCalculatorForm()
    
    if request.method == 'GET':
        stats = get_shop_stats(current_user.store_id)
        form.num_techs.data = stats['tech_count']
        form.proficiency.data = round(stats['proficiency'], 1)
        form.days_in_month.data = round(stats['work_days'], 1)

    results = None
    if form.validate_on_submit():
        daily_capacity_hours = form.num_techs.data * 8 * (form.proficiency.data / 100.0)
        monthly_capacity_hours = daily_capacity_hours * form.days_in_month.data
        
        raw_daily_ro_goal = daily_capacity_hours / form.avg_hours_per_ro.data
        daily_ro_capacity = math.ceil(raw_daily_ro_goal)
        
        walk_in = form.walk_in_percent.data
        if walk_in > 1: walk_in = walk_in / 100.0
            
        show_rate = form.show_rate.data
        if show_rate > 1: show_rate = show_rate / 100.0
        
        appt_ros_needed = daily_ro_capacity * (1 - walk_in)
        daily_appt_goal = math.ceil(appt_ros_needed / show_rate)
        
        results = {
            'daily_capacity_hours': daily_capacity_hours,
            'monthly_capacity_hours': monthly_capacity_hours,
            'daily_ro_goal': daily_ro_capacity,
            'monthly_ro_goal': daily_ro_capacity * form.days_in_month.data,
            'daily_appt_goal': daily_appt_goal
        }
        
    return render_template('calculators/appointment.html', form=form, results=results, title="RO & Appointment Calculator")

@calculators_bp.route('/calculators/cpgp', methods=['GET', 'POST'])
@login_required
def cpgp_calculator():
    form = CPGPOpportunityForm()
    
    if request.method == 'GET':
        stats = get_shop_stats(current_user.store_id)
        # 1. Current State - Aligned with Shop Stats & MPI Logic
        form.curr_elr.data = stats['elr']
        form.curr_labor_margin.data = stats['labor_margin']
        form.curr_parts_ratio.data = stats['parts_ratio']
        form.curr_parts_margin.data = stats['parts_margin']
        
        # Standard Baseline: 2.0 Hours/RO (Consistent with MPI/Appt Calcs)
        baseline_hours_per_ro = 2.0
        form.curr_hours_per_ro.data = baseline_hours_per_ro
        
        # Calculate RO Count based on Capacity (Same as MPI)
        if stats['tech_count'] > 0:
            daily_cap_hours = stats['tech_count'] * 8 * (stats['proficiency'] / 100.0)
            monthly_cap_hours = daily_cap_hours * stats['work_days']
            form.curr_ro_count.data = int(monthly_cap_hours / baseline_hours_per_ro)
        else:
            form.curr_ro_count.data = 0
        
        # 2. Opportunity State (Pre-fill with Current for easy What-If)
        form.opp_elr.data = stats['elr']
        form.opp_labor_margin.data = stats['labor_margin']
        form.opp_parts_ratio.data = stats['parts_ratio']
        form.opp_parts_margin.data = stats['parts_margin']
        form.opp_hours_per_ro.data = baseline_hours_per_ro
        form.opp_ro_count.data = form.curr_ro_count.data

    results = None
    if form.validate_on_submit():
        def calc_metrics(elr, hrs, l_margin, p_ratio, p_margin, count):
            labor_sales = elr * hrs
            labor_gp = labor_sales * (l_margin / 100.0)
            parts_sales = labor_sales * p_ratio
            parts_gp = parts_sales * (p_margin / 100.0)
            total_gp_ro = labor_gp + parts_gp
            total_monthly_gp = total_gp_ro * count
            return total_gp_ro, total_monthly_gp

        curr_ro, curr_total = calc_metrics(
            form.curr_elr.data, form.curr_hours_per_ro.data, form.curr_labor_margin.data,
            form.curr_parts_ratio.data, form.curr_parts_margin.data, form.curr_ro_count.data
        )
        
        opp_ro, opp_total = calc_metrics(
            form.opp_elr.data, form.opp_hours_per_ro.data, form.opp_labor_margin.data,
            form.opp_parts_ratio.data, form.opp_parts_margin.data, form.opp_ro_count.data
        )
        
        results = {
            'current_gp_ro': curr_ro,
            'opportunity_gp_ro': opp_ro,
            'variance_ro': opp_ro - curr_ro,
            'current_monthly_gp': curr_total,
            'opportunity_monthly_gp': opp_total,
            'monthly_variance': opp_total - curr_total,
            'yearly_variance': (opp_total - curr_total) * 12
        }
        
    return render_template('calculators/cpgp.html', form=form, results=results, title="CP Gross Profit Opportunity")

@calculators_bp.route('/calculators/capacity', methods=['GET', 'POST'])
@login_required
def capacity_calculator():
    form = CapacityOpportunityForm()
    
    if request.method == 'GET':
        stats = get_shop_stats(current_user.store_id)
        
        form.curr_tech_count.data = stats['tech_count']
        form.curr_proficiency.data = round(stats['proficiency'], 1)
        form.curr_elr.data = stats['elr']
        form.curr_labor_margin.data = stats['labor_margin']
        form.curr_parts_ratio.data = stats['parts_ratio']
        form.curr_parts_margin.data = stats['parts_margin']
        form.curr_unapplied.data = int(stats['unapplied'])
        
        # Use calculated Work Days
        form.days_in_month.data = round(stats['work_days'], 1)
        
        form.opp_tech_count.data = stats['tech_count']
        form.opp_proficiency.data = round(stats['proficiency'], 1)
        form.opp_elr.data = stats['elr']
        form.opp_labor_margin.data = stats['labor_margin']
        form.opp_parts_ratio.data = stats['parts_ratio']
        form.opp_parts_margin.data = stats['parts_margin']
        form.opp_unapplied.data = int(stats['unapplied'])

    results = None
    
    if form.validate_on_submit():
        def calc_forecast(techs, prof, days, hrs_day, elr, l_mgn, p_ratio, p_mgn, unapplied):
            total_hours = techs * hrs_day * (prof / 100.0) * days
            labor_sales = total_hours * elr
            labor_gp = (labor_sales * (l_mgn / 100.0)) - abs(unapplied)
            parts_sales = labor_sales * p_ratio
            parts_gp = parts_sales * (p_mgn / 100.0)
            return labor_gp, parts_gp, labor_gp + parts_gp

        curr_l, curr_p, curr_t = calc_forecast(
            form.curr_tech_count.data, form.curr_proficiency.data, form.days_in_month.data,
            form.hours_per_day.data, form.curr_elr.data, form.curr_labor_margin.data,
            form.curr_parts_ratio.data, form.curr_parts_margin.data, form.curr_unapplied.data
        )
        
        opp_l, opp_p, opp_t = calc_forecast(
            form.opp_tech_count.data, form.opp_proficiency.data, form.days_in_month.data,
            form.hours_per_day.data, form.opp_elr.data, form.opp_labor_margin.data,
            form.opp_parts_ratio.data, form.opp_parts_margin.data, form.opp_unapplied.data
        )
        
        results = {
            'current': {'labor': curr_l, 'parts': curr_p, 'total': curr_t},
            'opportunity': {'labor': opp_l, 'parts': opp_p, 'total': opp_t},
            'variance': opp_t - curr_t,
            'annualized': (opp_t - curr_t) * 12
        }
        
    return render_template('calculators/capacity.html', form=form, results=results, title="Service RO Opportunity Worksheet")

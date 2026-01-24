from datetime import date
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template, url_for, flash, redirect, request
from extensions import db, login_manager, bcrypt
from models import (
    User, Team, TeamMember, ScheduleEntry, WorkLog, TeamSchedule,
    ProductionObjectiveMemo, FinancialForecast, FinancialInputs # Import FinancialInputs
)
from forms import (
    RegistrationForm, LoginForm, TeamForm, TeamMemberForm, ScheduleEntryForm,
    WorkLogForm, TeamScheduleForm, RecurringScheduleForm, ScheduleEntryFilterForm,
    FinancialPerformanceForm
)
from flask_login import login_user, current_user, logout_user, login_required
from datetime import date, time, timedelta, datetime
import calendar
from collections import defaultdict
from flask_migrate import Migrate
from decimal import Decimal

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'a_very_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # Initialize Flask-Migrate here
    migrate = Migrate(app, db)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app

app = create_app()

# --- HELPER FUNCTIONS FOR HOME ROUTE ---

def calculate_weekly_financial_total(user_id):
    """Calculates the total financial forecast for the current week (Monday to Sunday)."""
    user_inputs = FinancialInputs.query.filter_by(user_id=user_id).first()
    
    # If no inputs are saved, return None
    if not user_inputs:
        return None

    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Convert percentage inputs to decimals
    elr = user_inputs.effective_labor_rate
    parts_to_labor_ratio = user_inputs.parts_to_labor_ratio
    # Assuming margins are stored as whole numbers (e.g., 50 for 50%) and need conversion
    labor_margin = user_inputs.labor_margin / 100
    parts_margin = user_inputs.parts_margin / 100

    # Get all scheduled entries for the current week
    weekly_schedules = ScheduleEntry.query.filter(
        ScheduleEntry.date >= start_of_week,
        ScheduleEntry.date <= end_of_week
    ).all()
    
    total_frh = 0.0
    for s in weekly_schedules:
        # Check if team_member and daily_production_objective exist
        if s.team_member and s.team_member.daily_production_objective is not None:
             total_frh += s.team_member.daily_production_objective
    
    if total_frh == 0:
        return {'expected_frh': 0.0, 'elr': elr, 'labor_gross': 0.0, 'parts_gross': 0.0, 'total_gross': 0.0}

    # Calculate gross based on total FRH and financial inputs
    labor_gross = total_frh * elr * labor_margin
    parts_gross = total_frh * elr * parts_to_labor_ratio * parts_margin
    total_gross = labor_gross + parts_gross
    
    # Return the dictionary used by home.html
    return {
        'expected_frh': total_frh,
        'elr': elr, # Pass ELR for KPI display
        'labor_gross': labor_gross,
        'parts_gross': parts_gross,
        'total_gross': total_gross
    }

def get_weekly_tech_schedules(user_id):
    """Fetches and organizes team member schedules for the current week."""
    
    # Calculate the start and end of the current week (Monday to Sunday)
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # Fetch all schedules for this week
    weekly_schedules = ScheduleEntry.query.filter(
        ScheduleEntry.date >= start_of_week,
        ScheduleEntry.date <= end_of_week
    ).order_by(ScheduleEntry.date, ScheduleEntry.start_time).all()

    # Dictionaries to process schedules
    member_weekly_summary = defaultdict(lambda: defaultdict(list))
    
    # Populate the member_weekly_summary
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    # Get all members and teams to ensure everyone is listed
    all_members = TeamMember.query.all()
    teams_dict = {team.id: team.name for team in Team.query.all()}
    
    # Process schedules
    for s in weekly_schedules:
        member = s.team_member
        if not member: continue
        
        member_name = member.name
        team_name = teams_dict.get(member.team_id, 'Unassigned')
        day_index = s.date.weekday()
        
        schedule_time = f"{s.start_time.strftime('%I:%M%p')}-{s.end_time.strftime('%I:%M%p')}"
        member_weekly_summary[team_name][member_name].append(f"{day_names[day_index]}: {schedule_time}")

    # Final structure for the template
    tech_schedules = defaultdict(list)
    
    # Consolidate schedules for all members
    for member in all_members:
        team_name = teams_dict.get(member.team_id, 'Unassigned')
        member_name = member.name
        
        if member_name in member_weekly_summary[team_name]:
            # Member has a schedule this week
            schedules = member_weekly_summary[team_name][member_name]
            tech_schedules[team_name].append({
                'name': member_name,
                'schedule': " | ".join(schedules)
            })
        else:
            # Member has no schedule this week
            tech_schedules[team_name].append({
                'name': member_name,
                'schedule': 'No Schedule'
            })

    return dict(tech_schedules)


# --- MAIN ROUTES ---

@app.route("/")
@app.route("/home")
@login_required
def home():
    # Fetch data for KPI and Schedule display
    weekly_financial_total = calculate_weekly_financial_total(current_user.id)
    tech_schedules = get_weekly_tech_schedules(current_user.id)
    
    return render_template('home.html', 
                           title='Home',
                           weekly_financial_total=weekly_financial_total,
                           tech_schedules=tech_schedules)
# Helper function to apply the adjustments from the FinancialInputs model
from decimal import Decimal

# Helper function to apply the adjustments from the FinancialInputs model
def apply_financial_adjustments(forecast_data, user_inputs):
    """
    Applies the various gross and cost adjustments to the base financial forecast,
    respecting that Unapplied Time is always a deduction.
    """
    from decimal import Decimal

    # Base Gross (from the daily forecast calculation)
    base_labor_gross = forecast_data.get('labor_gross', Decimal('0.00'))
    base_parts_gross = forecast_data.get('parts_gross', Decimal('0.00'))
    
    # --- Helper function for safe conversion ---
    def safe_decimal_input(value):
        """Safely converts potential None/number input to Decimal, defaults to 0."""
        return Decimal(str(value or 0))

    # --- Extract Adjustment Inputs (Converted using safe helper) ---
    
    # Other/Revenue Items (applied based on user input sign)
    other_ro_gross = safe_decimal_input(user_inputs.other_ro_gross)
    wholesale_gross = safe_decimal_input(user_inputs.wholesale_gross)
    parts_retail_gross = safe_decimal_input(user_inputs.parts_retail_gross)
    
    # Labor Deduction
    unapplied_time_cost = safe_decimal_input(user_inputs.unapplied_time_cost) 
    
    # Parts Adjustments (applied based on user input sign)
    parts_inventory_adjust = safe_decimal_input(user_inputs.parts_inventory_adjust)
    parts_allowance = safe_decimal_input(user_inputs.parts_allowance)
    purchase_discounts = safe_decimal_input(user_inputs.purchase_discounts)

    # -------------------------------------------------------------
    # --- 1. Calculate FINAL Adjusted Gross Totals for each category ---
    # -------------------------------------------------------------

    # 1. FINAL LABOR GROSS TOTAL
    # Unapplied time is ALWAYS a deduction, so we subtract its absolute value
    # to ensure it reduces labor gross, even if the user accidentally enters a negative number.
    final_labor_gross = base_labor_gross - abs(unapplied_time_cost)

    # 2. FINAL PARTS GROSS TOTAL
    # Parts adjustments are applied directly, respecting the user-inputted sign
    # (e.g., a positive "inventory adjust" is added, a negative is subtracted).
    parts_adjustments = (
        wholesale_gross + 
        parts_retail_gross + 
        parts_inventory_adjust + # Applied based on sign
        parts_allowance +        # Applied based on sign
        purchase_discounts       # Applied based on sign
    )
    final_parts_gross = base_parts_gross + parts_adjustments

    # 3. FINAL OTHER GROSS TOTAL
    # Other RO Gross is treated as its own miscellaneous bucket, applied based on sign.
    final_other_gross = other_ro_gross
    
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

@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    # --- Imports ---
    from decimal import Decimal
    from collections import defaultdict
    import calendar
    from datetime import date, timedelta, datetime
    
    # You MUST define default_forecast here
    default_forecast = {
        'labor_gross': Decimal('0.00'),
        'parts_gross': Decimal('0.00'),
        'other_gross': Decimal('0.00'),
        'total_gross': Decimal('0.00'),
        'expected_frh': Decimal('0.00'),
    }

    # Helper function to safely get Decimal values
    def safe_decimal(value):
        """Converts value to Decimal, treating None as Decimal(0)."""
        if value is None:
            return Decimal(0)
        return Decimal(str(value)) 

    # --- Initialization ---
    financial_data = defaultdict(lambda: default_forecast.copy())
    weekly_financial_total = default_forecast.copy()
    next_weekly_financial_total = default_forecast.copy()
    full_month_financial_forecast = default_forecast.copy()
    weekly_member_data = {}
    mtd_member_data = {}
    expected_frh_mtd = 0

    # 1. FETCH user_inputs ONCE
    user_inputs = FinancialInputs.query.filter_by(user_id=current_user.id).first()
    
    # 2. Initialize the form ONCE using the fetched data
    # This ensures the form is correctly populated with saved data on GET request/redirect.
    if user_inputs:
        financial_form = FinancialPerformanceForm(obj=user_inputs)
    else:
        financial_form = FinancialPerformanceForm()
    
    # --- POST Request: Saving Financial Inputs ---
    if request.method == 'POST':
        # Re-initialize the form from request.form for validation only.
        financial_form = FinancialPerformanceForm(request.form)
        if financial_form.validate_on_submit():
            
            # Create a new record if it doesn't exist (using the object fetched at the start)
            if not user_inputs:
                user_inputs = FinancialInputs(user_id=current_user.id)
                db.session.add(user_inputs)

            # --- Save ALL Financial Fields ---
            user_inputs.effective_labor_rate = financial_form.elr.data
            user_inputs.parts_to_labor_ratio = financial_form.parts_to_labor_ratio.data
            user_inputs.labor_margin = financial_form.labor_margin.data
            user_inputs.parts_margin = financial_form.parts_margin.data
            
            # Adjustment Fields
            user_inputs.other_ro_gross = financial_form.other_ro_gross.data
            user_inputs.unapplied_time_cost = financial_form.unapplied_time_cost.data
            user_inputs.parts_inventory_adjust = financial_form.parts_inventory_adjust.data
            user_inputs.parts_allowance = financial_form.parts_allowance.data
            user_inputs.purchase_discounts = financial_form.purchase_discounts.data
            user_inputs.wholesale_gross = financial_form.wholesale_gross.data
            user_inputs.parts_retail_gross = financial_form.parts_retail_gross.data
                
            db.session.commit()
            # CRITICAL: Expire the object to force a fresh load on the next GET request
            db.session.expire(user_inputs)
            
            flash('Financial inputs updated successfully!', 'success')
            return redirect(url_for('dashboard')) 

    # --- GET Request & Calculations (Only run if user inputs exist) ---
    if user_inputs:
        
        # 🛑 FIX: The line 'financial_form = FinancialPerformanceForm(obj=user_inputs)' 
        # has been removed from here, as it was redundant and caused the issue.

        # 2. Extract SAFE Decimal values for calculation
        elr = safe_decimal(user_inputs.effective_labor_rate)
        parts_to_labor_ratio = safe_decimal(user_inputs.parts_to_labor_ratio)
        labor_margin = safe_decimal(user_inputs.labor_margin) / Decimal(100)
        parts_margin = safe_decimal(user_inputs.parts_margin) / Decimal(100)

        # Timeframes (Moved inside to ensure they are defined for calculations)
        today = date.today()
        start_of_month = today.replace(day=1)
        end_of_month = date.fromordinal(start_of_month.toordinal() + calendar.monthrange(today.year, today.month)[1] - 1)
        
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        start_of_next_week = start_of_week + timedelta(days=7)
        end_of_next_week = start_of_next_week + timedelta(days=6)
        
        # 3. Daily Forecast (financial_data) - Uses calculation variables above
        all_schedules_in_range = ScheduleEntry.query.filter(
            ScheduleEntry.date >= start_of_month, 
            ScheduleEntry.date <= end_of_next_week
        ).all()
        
        financial_data = defaultdict(lambda: default_forecast.copy())
        
        for s in all_schedules_in_range:
            member = TeamMember.query.get(s.team_member_id)
            if member and member.daily_production_objective is not None:
                expected_frh_day = safe_decimal(member.daily_production_objective)
                
                # Calculations using saved ELR
                labor_gross = expected_frh_day * elr * labor_margin
                parts_gross = expected_frh_day * elr * parts_to_labor_ratio * parts_margin
                total_gross = labor_gross + parts_gross
                
                financial_data[s.date]['labor_gross'] += labor_gross
                financial_data[s.date]['parts_gross'] += parts_gross
                financial_data[s.date]['total_gross'] += total_gross
                financial_data[s.date]['expected_frh'] += expected_frh_day
        
        # 4. Weekly Forecast Totals (Summing the daily data)
        weekly_financial_total = default_forecast.copy()
        next_weekly_financial_total = default_forecast.copy()

        for d, data in financial_data.items():
            if start_of_week <= d <= end_of_week:
                for k, v in data.items():
                    weekly_financial_total[k] += v
            
            if start_of_next_week <= d <= end_of_next_week:
                for k, v in data.items():
                    next_weekly_financial_total[k] += v

        # 5. Full Month Forecast (Base + Adjustments)
        base_month_total = default_forecast.copy()
        for d, data in financial_data.items():
            if start_of_month <= d <= end_of_month:
                for k, v in data.items():
                    base_month_total[k] += v

        full_month_financial_forecast = apply_financial_adjustments(base_month_total, user_inputs)
        
        # 6. Save the forecast to the database (Uses date/timeframe variables)
        forecast_entry = FinancialForecast.query.filter_by(month=today.month, year=today.year).first()
        if not forecast_entry:
            forecast_entry = FinancialForecast(
                month=today.month,
                year=today.year,
                labor_gross=full_month_financial_forecast['labor_gross'],
                parts_gross=full_month_financial_forecast['parts_gross'],
                total_gross=full_month_financial_forecast['total_gross'],
                expected_frh=full_month_financial_forecast['expected_frh']
            )
            db.session.add(forecast_entry)
        else:
            forecast_entry.labor_gross = full_month_financial_forecast['labor_gross']
            forecast_entry.parts_gross = full_month_financial_forecast['parts_gross']
            forecast_entry.total_gross = full_month_financial_forecast['total_gross']
            forecast_entry.expected_frh = full_month_financial_forecast['expected_frh']
            forecast_entry.date_updated = date.today()
            
        db.session.commit()
    
    # --- MTD Member Data (Runs regardless of financial inputs) ---
    # Ensure date variables are defined for MTD logic if they weren't inside 'if user_inputs:'
    if 'today' not in locals():
        today = date.today()
        start_of_month = today.replace(day=1)

    all_members = TeamMember.query.all()
    members_dict = {member.id: member for member in all_members}
    
    # ... (Your existing MTD member calculation logic, properly using 'today' and 'start_of_month') ...
    # (The MTD loop is omitted for brevity but should be here)

    # Recalculate expected_frh_mtd
    expected_frh_mtd = sum(s.team_member.daily_production_objective for s in ScheduleEntry.query.filter(ScheduleEntry.date >= start_of_month, ScheduleEntry.date <= today).all() if s.team_member and s.team_member.daily_production_objective is not None)
    # 🛑 FINAL FIX: Manually overwrite form data to guarantee the saved value displays.
    if user_inputs:
        financial_form.elr.data = user_inputs.effective_labor_rate
        financial_form.parts_to_labor_ratio.data = user_inputs.parts_to_labor_ratio
        # Repeat for all other input fields...
        financial_form.labor_margin.data = user_inputs.labor_margin
        financial_form.parts_margin.data = user_inputs.parts_margin
        financial_form.other_ro_gross.data = user_inputs.other_ro_gross
        financial_form.unapplied_time_cost.data = user_inputs.unapplied_time_cost
        financial_form.parts_inventory_adjust.data = user_inputs.parts_inventory_adjust
        financial_form.parts_allowance.data = user_inputs.parts_allowance
        financial_form.purchase_discounts.data = user_inputs.purchase_discounts
        financial_form.wholesale_gross.data = user_inputs.wholesale_gross
        financial_form.parts_retail_gross.data = user_inputs.parts_retail_gross
        
    # --- Render Template (Final Context) ---
    # Ensure all date variables are available for the template context
    if 'start_of_week' not in locals():
        start_of_week = date.today()
        end_of_week = date.today()
        start_of_next_week = date.today()
        end_of_next_week = date.today()
    
    return render_template('dashboard.html',
                            title='Dashboard',
                            weekly_member_data=weekly_member_data, 
                            mtd_member_data=mtd_member_data, 
                            financial_form=financial_form,
                            expected_frh_mtd=expected_frh_mtd,
                            financial_data=financial_data,
                            weekly_financial_total=weekly_financial_total,
                            next_weekly_financial_total=next_weekly_financial_total,
                            full_month_financial_forecast=full_month_financial_forecast,
                            current_week_dates=f"{start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d')}",
                            next_week_dates=f"{start_of_next_week.strftime('%b %d')} - {end_of_next_week.strftime('%b %d')}",
                            team_members=members_dict)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login')) # Redirect to login page instead of home
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/teams", methods=['GET', 'POST'])
@login_required
def teams():
    form = TeamForm()
    
    if form.validate_on_submit():
        team = Team(name=form.name.data)
        db.session.add(team)
        db.session.commit()
        flash('Team created successfully!', 'success')
        return redirect(url_for('teams'))

    all_teams = Team.query.all()
    
    return render_template('teams.html', title='Teams', form=form, all_teams=all_teams)

@app.route("/team/new", methods=['GET', 'POST'])
@login_required
def new_team():
    form = TeamForm()
    if form.validate_on_submit():
        team = Team(name=form.name.data)
        db.session.add(team)
        db.session.commit()
        flash('Team created successfully!', 'success')
        return redirect(url_for('teams')) # Redirect to teams overview
    return render_template('create_edit_team.html', title='New Team', form=form)

@app.route("/team/<int:team_id>/add_member", methods=['GET', 'POST'])
@login_required
def add_member_to_team(team_id):
    team = Team.query.get_or_404(team_id)
    form = TeamMemberForm()
    # Pre-select the team in the form
    form.team.data = team

    if form.validate_on_submit():
        new_member = TeamMember(
            name=form.name.data,
            team_id=team.id,
            tech_level=form.tech_level.data,
            daily_production_objective=form.daily_production_objective.data
        )
        db.session.add(new_member)
        db.session.commit()
        flash(f'Team member {new_member.name} added to {team.name} successfully!', 'success')
        return redirect(url_for('teams'))

    return render_template('add_member_to_team.html', title=f'Add Member to {team.name}', form=form, team=team)

@app.route("/team/<int:team_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_team(team_id):
    team = Team.query.get_or_404(team_id)
    form = TeamForm(obj=team)
    if form.validate_on_submit():
        team.name = form.name.data
        db.session.commit()
        flash('Team updated successfully!', 'success')
        return redirect(url_for('teams'))
    return render_template('create_edit_team.html', title='Edit Team', form=form)

@app.route("/team/<int:team_id>/delete", methods=['POST'])
@login_required
def delete_team(team_id):
    team = Team.query.get_or_404(team_id)
    db.session.delete(team)
    db.session.commit()
    flash('Team deleted successfully!', 'success')
    return redirect(url_for('teams'))

@app.route("/team_members", methods=['GET', 'POST'])
@login_required
def team_members():
    form = TeamMemberForm()
    
    if form.validate_on_submit():
        selected_team = form.team.data
        
        new_member = TeamMember(
            name=form.name.data,
            team_id=selected_team.id if selected_team else None,
            tech_level=form.tech_level.data,
            daily_production_objective=form.daily_production_objective.data
        )
        db.session.add(new_member)
        db.session.commit()
        flash('Team member added successfully!', 'success')
        return redirect(url_for('team_members'))
    
    all_members = TeamMember.query.all()
    
    return render_template('team_members.html', form=form, team_members=all_members)

@app.route("/team_member/<int:member_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_team_member(member_id):
    member = TeamMember.query.get_or_404(member_id)
    form = TeamMemberForm(obj=member)
    
    if form.validate_on_submit():
        # Check if objective has changed to create a memo
        if form.daily_production_objective.data != member.daily_production_objective:
            memo = ProductionObjectiveMemo(
                team_member_id=member.id,
                previous_objective=member.daily_production_objective
            )
            db.session.add(memo)

        member.name = form.name.data
        member.team = form.team.data
        member.tech_level = form.tech_level.data
        member.daily_production_objective = form.daily_production_objective.data
        
        db.session.commit()
        flash('Team Member updated successfully!', 'success')
        return redirect(url_for('team_members'))
        
    return render_template('create_edit_team_member.html', title='Edit Team Member', form=form)

@app.route("/team_member/<int:member_id>/delete", methods=['POST'])
@login_required
def delete_team_member(member_id):
    member = TeamMember.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    flash('Team Member deleted successfully!', 'success')
    return redirect(url_for('team_members')) # Redirect to team members overview

@app.route("/schedules", methods=['GET'])
@login_required
def schedules():
    # 1. Initialize the filter form with GET request arguments
    filter_form = ScheduleEntryFilterForm(request.args)
    
    # --- Date Filtering Logic ---
    today = date.today()
    target_year = today.year
    target_month = today.month
    
    # Check if a month was selected in the filter form
    if filter_form.month_filter.data:
        try:
            # The value from the form is expected to be 'YYYY-MM'
            year_str, month_str = filter_form.month_filter.data.split('-')
            target_year = int(year_str)
            target_month = int(month_str)
        except ValueError:
            # Handle invalid data, default back to current month
            pass

    # Ensure the dropdown reflects the month being viewed (important on initial load)
    filter_form.month_filter.data = f"{target_year:04d}-{target_month:02d}"

    # Calculate the start and end dates for the target month
    start_date = date(target_year, target_month, 1)
    
    # Calculate the last day of the month using relativedelta
    end_date = start_date + relativedelta(months=1) - timedelta(days=1)
    # ----------------------------

    # Start the query, joining necessary tables for filtering and grouping
    query = ScheduleEntry.query.join(ScheduleEntry.team_member).join(TeamMember.team)
    
    # 2. Apply Date Filter (CRITICAL FIX)
    query = query.filter(
        ScheduleEntry.date >= start_date,
        ScheduleEntry.date <= end_date
    )
    
    # 3. Apply Team/Member Filtering based on form data (using request.args/form.data on GET)
    if filter_form.validate():
        # Filter by Team 
        if filter_form.team.data and filter_form.team.data.id:
            team_id_to_filter = filter_form.team.data.id
            query = query.filter(TeamMember.team_id == team_id_to_filter)
            
        # Filter by Tech/Team Member
        if filter_form.team_member.data and filter_form.team_member.data.id:
            member_id = filter_form.team_member.data.id
            query = query.filter(ScheduleEntry.team_member_id == member_id)

    # 4. Order the data for display: Team -> Date -> Tech Name
    all_entries = query.order_by(
        Team.name,
        ScheduleEntry.date,
        TeamMember.name
    ).all()
    
    # 5. Structure Data: Nested dictionary {TeamName: {Date: [Entries]}}
    team_schedule = defaultdict(lambda: defaultdict(list))
    
    for entry in all_entries:
        team_name = entry.team_member.team.name
        # Use date as a string for dictionary keys 
        date_str = entry.date.strftime('%Y-%m-%d')
        
        team_schedule[team_name][date_str].append(entry)
        
    # Pass the structured dictionary and the form to the template
    return render_template('schedules.html', 
                           title=f'Team Schedules for {start_date.strftime("%B %Y")}', # Update title
                           team_schedule=team_schedule, 
                           filter_form=filter_form)

@app.route("/schedule_calendar")
@login_required
def schedule_calendar():
    all_schedules = ScheduleEntry.query.order_by(ScheduleEntry.date, ScheduleEntry.start_time).all()
    
    events = []
    for schedule in all_schedules:
        # Combine date and time to create datetime objects
        start_datetime = datetime.combine(schedule.date, schedule.start_time) if schedule.start_time else datetime.combine(schedule.date, time(8, 0))
        end_datetime = datetime.combine(schedule.date, schedule.end_time) if schedule.end_time else datetime.combine(schedule.date, time(17, 0))
        
        # Create a title for the event
        title = f"{schedule.team_member.name} ({start_datetime.strftime('%I:%M %p')}-{end_datetime.strftime('%I:%M %p')})" if schedule.team_member else "Unassigned Schedule"
        
        events.append({
            'title': title,
            'start': start_datetime.isoformat(),
            'end': end_datetime.isoformat(),
            'notes': schedule.notes
        })

    return render_template('schedule_calendar.html', 
                            title='Schedule Calendar', 
                            events=events)

@app.route("/schedule/new", methods=['GET', 'POST'])
@login_required
def new_schedule_entry():
    form = ScheduleEntryForm()
    if form.validate_on_submit():
        entry = ScheduleEntry(
            team_member=form.team_member.data,
            date=form.date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            lunch_start=form.lunch_start.data,
            lunch_end=form.lunch_end.data,
            notes=form.notes.data
        )
        db.session.add(entry)
        db.session.commit()
        flash('Schedule entry created successfully!', 'success')
        return redirect(url_for('schedules'))
    return render_template('create_edit_schedule_entry.html', title='New Schedule Entry', form=form)

@app.route("/schedule/<int:entry_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_schedule_entry(entry_id):
    entry = ScheduleEntry.query.get_or_404(entry_id)
    form = ScheduleEntryForm(obj=entry)
    if form.validate_on_submit():
        entry.team_member = form.team_member.data
        entry.date = form.date.data
        entry.start_time = form.start_time.data
        entry.end_time = form.end_time.data
        entry.lunch_start = form.lunch_start.data
        entry.lunch_end = form.lunch_end.data
        entry.notes = form.notes.data
        db.session.commit()
        flash('Schedule entry updated successfully!', 'success')
        return redirect(url_for('schedules'))
    return render_template('create_edit_schedule_entry.html', title='Edit Schedule Entry', form=form)

@app.route("/schedule/<int:entry_id>/delete", methods=['POST'])
@login_required
def delete_schedule_entry(entry_id):
    entry = ScheduleEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash('Schedule entry deleted successfully!', 'success')
    return redirect(url_for('schedules'))

@app.route("/team_schedules")
@login_required
def team_schedules():
    all_team_schedules = TeamSchedule.query.order_by(TeamSchedule.team_id, TeamSchedule.day_of_week).all()
    
    return render_template('team_schedules.html', 
                            title='Team Schedules', 
                            team_schedules=all_team_schedules)

@app.route("/work_logs")
@login_required
def work_logs():
    """Route to view all recorded work logs."""
    # Fetch all logs, usually ordered by date descending
    all_logs = WorkLog.query.order_by(WorkLog.date.desc()).all()
    return render_template('work_logs.html', title='Work Logs', work_logs=all_logs)

# --------------------------------------------------------------------------

@app.route("/work_logs/new", methods=['GET', 'POST'])
@login_required
def new_work_log():
    form = WorkLogForm()
    
    # 🛑 DEBUG 1: Check if the request is a POST submission
    if request.method == 'POST':
        print("--- DEBUG: POST Request Received ---")

    if form.validate_on_submit():
        
        # 🛑 DEBUG 2: Check the hours value BEFORE creating the object
        print(f"--- DEBUG: Form Validation SUCCESS ---")
        print(f"Hours to save: {form.flat_rate_hours.data}") 
        
        new_log = WorkLog(
            team_member_id=form.team_member.data.id,
            date=form.date.data,
            start_time=form.start_time.data, # 🛑 THIS MUST BE PRESENT AND CORRECT
            end_time=form.end_time.data,
            ro_number=form.ro_number.data,        # <-- Use the cleaned variable
            line_item=form.line_item.data,
            flat_rate_hours=form.flat_rate_hours.data, 
            notes=form.notes.data
        )
        
        db.session.add(new_log)
        
        # 🛑 DEBUG 3: Check BEFORE committing
        print("--- DEBUG: Committing to database ---")
        
        try:
            db.session.commit()
            print("--- DEBUG: Commit SUCCESS ---")
        except Exception as e:
            db.session.rollback()
            print(f"--- DEBUG: Commit FAILED with error: {e} ---")
            flash(f"Database Error: {e}", 'danger')
            
        flash('New work log created successfully!', 'success')
        return redirect(url_for('work_logs'))
        
    # If validation fails, we can check for errors here
    elif request.method == 'POST':
        print("--- DEBUG: Form Validation FAILED ---")
        for field, errors in form.errors.items():
            print(f"Field: {field}, Errors: {errors}")
            
    return render_template('create_edit_work_log.html', title='New Work Log', form=form)

# --------------------------------------------------------------------------

@app.route("/work_log/<int:log_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_work_log(log_id):
    """Route to edit an existing work log entry."""
    log = WorkLog.query.get_or_404(log_id)
    # Pass the log object to the form to pre-populate fields on GET
    form = WorkLogForm(obj=log) 
    
    if form.validate_on_submit():
        
        # 🛑 CRITICAL FIX: Update the foreign key (team_member_id) directly
        log.team_member_id = form.team_member.data.id 
        
        # Update the rest of the fields from the form data
        log.date = form.date.data
        log.start_time = form.start_time.data
        log.end_time = form.end_time.data
        log.ro_number = form.ro_number.data
        log.line_item = form.line_item.data
        
        # The hours field update
        log.flat_rate_hours = form.flat_rate_hours.data 
        
        log.notes = form.notes.data
        
        db.session.commit()
        flash('Work log updated successfully!', 'success')
        return redirect(url_for('work_logs'))
        
    # Handles GET request or failed POST (validation errors)
    return render_template('create_edit_work_log.html', title='Edit Work Log', form=form)

@app.route("/team_schedule/new", methods=['GET', 'POST'])
@login_required
def new_team_schedule():
    form = TeamScheduleForm()
    if form.validate_on_submit():
        schedule = TeamSchedule(
            team=form.team.data,
            day_of_week=form.day_of_week.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            lunch_start=form.lunch_start.data,
            lunch_end=form.lunch_end.data,
            notes=form.notes.data
        )
        db.session.add(schedule)
        db.session.commit()
        flash('Team schedule created successfully!', 'success')
        return redirect(url_for('team_schedules'))
    return render_template('create_edit_team_schedule.html', title='New Team Schedule', form=form)


@app.route("/team_schedule/<int:schedule_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_team_schedule(schedule_id):
    schedule = TeamSchedule.query.get_or_404(schedule_id)
    form = TeamScheduleForm(obj=schedule)
    if form.validate_on_submit():
        schedule.team = form.team.data
        schedule.day_of_week = form.day_of_week.data
        schedule.start_time = form.start_time.data
        schedule.end_time = form.end_time.data
        schedule.lunch_start = form.lunch_start.data
        schedule.lunch_end = form.lunch_end.data
        schedule.notes = form.notes.data
        db.session.commit()
        flash('Team schedule updated successfully!', 'success')
        return redirect(url_for('team_schedules'))
    return render_template('create_edit_team_schedule.html', title='Edit Team Schedule', form=form)

@app.route("/work_log/<int:log_id>/delete", methods=['POST'])
@login_required
def delete_work_log(log_id):
    """Deletes a work log entry based on its ID."""
    
    # 1. Fetch the log or raise 404
    log = WorkLog.query.get_or_404(log_id)
    
    # 2. Delete and commit
    db.session.delete(log)
    db.session.commit()
    
    # 3. Flash success message and redirect
    flash('Work log deleted successfully!', 'success')
    return redirect(url_for('work_logs'))

@app.route("/team_schedule/<int:schedule_id>/delete", methods=['POST'])
@login_required
def delete_team_schedule(schedule_id):
    schedule = TeamSchedule.query.get_or_404(schedule_id)
    db.session.delete(schedule)
    db.session.commit()
    flash('Team schedule deleted successfully!', 'success')
    return redirect(url_for('team_schedules'))

@app.route("/generate_schedule", methods=['GET', 'POST'])
@login_required
def generate_schedule():
    form = RecurringScheduleForm()
    created_schedules = None

    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        days_of_week = form.days_of_week.data
        
        team_members_to_schedule = []
        flash_message_target = ""

        if form.team_member.data:
            member = TeamMember.query.get(form.team_member.data.id)
            if member:
                team_members_to_schedule.append(member)
                flash_message_target = member.name
        elif form.team.data:
            selected_team = Team.query.get(form.team.data.id)
            if selected_team:
                team_members_to_schedule = selected_team.members
                flash_message_target = selected_team.name
        else:
            flash('You must select either a team or a team member.', 'danger')
            return render_template('generate_schedules.html', title='Generate Schedule', form=form)

        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() in days_of_week:
                for member in team_members_to_schedule:
                    existing_entry = ScheduleEntry.query.filter_by(team_member_id=member.id, date=current_date).first()
                    if not existing_entry:
                        new_entry = ScheduleEntry(
                            team_member=member,
                            date=current_date,
                            start_time=form.start_time.data,
                            end_time=form.end_time.data,
                            lunch_start=form.lunch_start.data,
                            lunch_end=form.lunch_end.data,
                            notes=form.notes.data
                        )
                        db.session.add(new_entry)
            current_date += timedelta(days=1)
        
        db.session.commit()
        flash(f'Schedules for {flash_message_target} generated successfully!', 'success')
        
        created_schedules = ScheduleEntry.query.filter(
            ScheduleEntry.team_member_id.in_([member.id for member in team_members_to_schedule]),
            ScheduleEntry.date >= start_date,
            ScheduleEntry.date <= end_date
        ).order_by(ScheduleEntry.date).all()
        
    return render_template('generate_schedules.html', 
                            title='Generate Schedule', 
                            form=form, 
                            created_schedules=created_schedules)

@app.route("/monthly_forecast")
@login_required
def monthly_forecast():
    all_forecasts = FinancialForecast.query.order_by(FinancialForecast.year.desc(), FinancialForecast.month.desc()).all()
    
    return render_template('monthly_forecast.html', 
                            title='Monthly Forecast',
                            all_forecasts=all_forecasts)


if __name__ == '__main__':
    # You might want to remove debug=True in a production environment
    app.run(debug=True)

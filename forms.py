from flask_wtf import FlaskForm
from wtforms import (
    StringField, SubmitField, SelectMultipleField, widgets,
    TimeField, DateField, TextAreaField, PasswordField,
    BooleanField, DecimalField, SelectField, FloatField, HiddenField,
    RadioField, IntegerField, DateTimeLocalField
)
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Optional, NumberRange
from wtforms_sqlalchemy.fields import QuerySelectField
from models import User, Team, TeamMember, ASM
from datetime import date

# --- Query Factories & Helpers ---
def team_query():
    return Team.query.order_by(Team.name).all()

def team_member_query():
    return TeamMember.query.order_by(TeamMember.name).all()

def asm_query():
    return ASM.query.order_by(ASM.name).all()

# HELPER: Formats dropdowns as "Name (#123)"
def get_member_label(member):
    if member.tech_number:
        return f"{member.name} (#{member.tech_number})"
    return member.name

# ==========================================
# AUTHENTICATION FORMS
# ==========================================
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UserCreationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    roles = SelectMultipleField("Roles", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Create User")

# ==========================================
# ONBOARDING & SETTINGS FORMS
# ==========================================
class OnboardingForm(FlaskForm):
    # 1. Account Setup
    store_name = StringField('Dealership / Store Name', validators=[DataRequired()])
    username = StringField('Manager Username', validators=[DataRequired(), Length(min=4)])
    password = PasswordField('Create Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    # 2. Facility
    bays_with_lifts = IntegerField('Bays with Lifts', validators=[Optional()])
    bays_without_lifts = IntegerField('Bays without Lifts', validators=[Optional()])

    # 3. Financial Baseline (Overall)
    elr = DecimalField('Overall Effective Labor Rate ($)', places=2, validators=[DataRequired()])
    parts_to_labor = DecimalField('Overall Parts to Labor Ratio', places=2, validators=[DataRequired()])
    labor_margin = DecimalField('Overall Labor Margin %', places=1, validators=[DataRequired()])
    parts_margin = DecimalField('Overall Parts Margin %', places=1, validators=[DataRequired()])

    # 4. Customer Pay (CP) Baseline
    cp_elr = DecimalField('CP Effective Labor Rate ($)', places=2, validators=[Optional()])
    cp_parts_to_labor = DecimalField('CP Parts to Labor Ratio', places=2, validators=[Optional()])
    cp_labor_margin = DecimalField('CP Labor Margin %', places=1, validators=[Optional()])
    cp_parts_margin = DecimalField('CP Parts Margin %', places=1, validators=[Optional()])

    # 5. Adjustments & KPIs
    other_ro_gross = FloatField('Other RO Gross (+/- $)', validators=[Optional()])
    unapplied_time_cost = FloatField('Unapplied Time Cost ($)', validators=[Optional()])

    wholesale_gross = FloatField('Wholesale Gross', validators=[Optional()])
    parts_retail_gross = FloatField('Parts Retail Gross', validators=[Optional()])
    parts_inventory_adjust = FloatField('Parts Inv Adjust', validators=[Optional()])
    parts_allowance = FloatField('Parts Allowance', validators=[Optional()])
    purchase_discounts = FloatField('Purchase Discounts', validators=[Optional()])

    parts_fill_rate = FloatField('Parts Fill Rate %', validators=[Optional()])
    parts_turn_rate = FloatField('Parts Turn Rate', validators=[Optional()])

    submit = SubmitField('Launch My Dashboard')

class StoreSettingsForm(FlaskForm):
    # 1. Store Identity
    store_name = StringField('Dealership / Store Name', validators=[DataRequired()])

    # 2. Facility
    bays_with_lifts = IntegerField('Bays with Lifts', validators=[Optional()])
    bays_without_lifts = IntegerField('Bays without Lifts', validators=[Optional()])

    # 3. Financial Baseline (Overall)
    elr = DecimalField('Overall Effective Labor Rate ($)', places=2, validators=[DataRequired()])
    parts_to_labor = DecimalField('Overall Parts to Labor Ratio', places=2, validators=[DataRequired()])
    labor_margin = DecimalField('Overall Labor Margin %', places=1, validators=[DataRequired()])
    parts_margin = DecimalField('Overall Parts Margin %', places=1, validators=[DataRequired()])

    # 4. Customer Pay (CP) Baseline
    cp_elr = DecimalField('CP Effective Labor Rate ($)', places=2, validators=[Optional()])
    cp_parts_to_labor = DecimalField('CP Parts to Labor Ratio', places=2, validators=[Optional()])
    cp_labor_margin = DecimalField('CP Labor Margin %', places=1, validators=[Optional()])
    cp_parts_margin = DecimalField('CP Parts Margin %', places=1, validators=[Optional()])

    # 5. Adjustments & KPIs
    other_ro_gross = FloatField('Other RO Gross (+/- $)', validators=[Optional()])
    unapplied_time_cost = FloatField('Unapplied Time Cost ($)', validators=[Optional()])

    wholesale_gross = FloatField('Wholesale Gross', validators=[Optional()])
    parts_retail_gross = FloatField('Parts Retail Gross', validators=[Optional()])
    parts_inventory_adjust = FloatField('Parts Inv Adjust', validators=[Optional()])
    parts_allowance = FloatField('Parts Allowance', validators=[Optional()])
    purchase_discounts = FloatField('Purchase Discounts', validators=[Optional()])

    parts_fill_rate = FloatField('Parts Fill Rate %', validators=[Optional()])
    parts_turn_rate = FloatField('Parts Turn Rate', validators=[Optional()])

    submit = SubmitField('Update Store Settings')

class BulkTeamUploadForm(FlaskForm):
    # File Upload
    csv_file = FileField('Upload Team CSV', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV Files Only!')
    ])

    # Standard Schedule Defaults
    default_start_time = TimeField('Default Start Time', validators=[DataRequired()])
    default_end_time = TimeField('Default End Time', validators=[DataRequired()])
    default_lunch_start = TimeField('Default Lunch Start', validators=[Optional()])
    default_lunch_end = TimeField('Default Lunch End', validators=[Optional()])

    submit = SubmitField('Import Team Structure')

# ==========================================
# TEAM, MEMBER, AND ASM FORMS
# ==========================================
class TeamForm(FlaskForm):
    name = StringField('Team Name', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Save Team')

    def validate_name(self, name):
        team = Team.query.filter(Team.name == name.data).first()
        if team:
            instance = getattr(self, '_obj', None)
            if instance and instance.id == team.id:
                pass
            else:
                raise ValidationError('A team with this name already exists.')

class ASMForm(FlaskForm):
    """Form to Create/Edit ASMs"""
    name = StringField('ASM Name', validators=[DataRequired(), Length(max=100)])
    asm_number = StringField('ASM Number', validators=[DataRequired(), Length(max=20)])
    team = QuerySelectField('Team', query_factory=team_query, get_label='name', validators=[DataRequired()])
    submit = SubmitField('Save ASM')

class TeamMemberForm(FlaskForm):
    name = StringField('Member Name', validators=[DataRequired(), Length(max=100)])
    tech_number = StringField('Tech Number', validators=[Optional(), Length(max=20)])
    team = QuerySelectField('Team', query_factory=team_query, get_label='name', allow_blank=True, blank_text='-- Unassigned --')
    tech_level = StringField('Tech Level (e.g., A, B, C)', validators=[Optional(), Length(max=50)])

    dpo_calculation_mode = RadioField('DPO Setting',
                                      choices=[('manual', 'Set DPO Manually'), ('calculated', 'Calculate DPO (Historical)')],
                                      default='manual',
                                      validators=[DataRequired()])
    daily_production_objective = FloatField('Manual DPO (FRH)', validators=[Optional(), NumberRange(min=0)])

    # Historical Data Fields
    hist_frh_total = FloatField('Historical Total FRH', validators=[Optional(), NumberRange(min=0)], default=80.0)
    hist_days_in_period = IntegerField('Historical Days', validators=[Optional(), NumberRange(min=1)], default=10)
    hist_training_days = IntegerField('Training Days', validators=[Optional(), NumberRange(min=0)], default=0)
    hist_vacation_days = IntegerField('Vacation Days', validators=[Optional(), NumberRange(min=0)], default=0)
    expected_lift_percent = FloatField('Expected Lift %', validators=[Optional(), NumberRange(min=0)], default=100.0)

    submit = SubmitField('Save Member')

# ==========================================
# SCHEDULE FORMS
# ==========================================
class ScheduleEntryForm(FlaskForm):
    # Using helper here to show numbers
    team_member = QuerySelectField('Team Member', query_factory=team_member_query, get_label=get_member_label, validators=[DataRequired()])

    schedule_type = SelectField(
        'Schedule Type',
        choices=[
            ('WORK', 'Work Day (Productive)'),
            ('PTO', 'PTO (Non-Productive)'),
            ('TRAINING', 'Training Day (Non-Productive)')
        ],
        validators=[DataRequired()],
        default='WORK'
    )

    date = DateField('Date', validators=[DataRequired()], default=date.today)
    start_time = TimeField('Start Time', validators=[Optional()])
    end_time = TimeField('End Time', validators=[Optional()])
    lunch_start = TimeField('Lunch Start', validators=[Optional()])
    lunch_end = TimeField('Lunch End', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Entry')

class TeamScheduleForm(FlaskForm):
    team = QuerySelectField('Team', query_factory=team_query, get_label='name', validators=[DataRequired()])
    day_of_week = SelectField('Day of Week', choices=[
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'),
        (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ], coerce=int, validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    lunch_start = TimeField('Lunch Start (Optional)', validators=[Optional()])
    lunch_end = TimeField('Lunch End (Optional)', validators=[Optional()])
    notes = TextAreaField('Notes (Optional)')
    submit = SubmitField('Save Team Schedule')

class RecurringScheduleForm(FlaskForm):
    team = QuerySelectField('Team', query_factory=team_query, get_label='name', allow_blank=True, blank_text='-- Select Team --')
    team_member = QuerySelectField('Team Member', query_factory=team_member_query, get_label=get_member_label, allow_blank=True, blank_text='-- Select Member --')
    start_date = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d', default=date.today)
    end_date = DateField('End Date', validators=[DataRequired()], format='%Y-%m-%d')
    days_of_week = SelectMultipleField(
        'Days of Week',
        choices=[(0, 'Mon'), (1, 'Tue'), (2, 'Wed'), (3, 'Thu'), (4, 'Fri'), (5, 'Sat'), (6, 'Sun')],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput(),
        coerce=int,
        validators=[Optional()]
    )
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    lunch_start = TimeField('Lunch Start (Optional)', validators=[Optional()])
    lunch_end = TimeField('Lunch End (Optional)', validators=[Optional()])
    notes = TextAreaField('Notes (Optional)')
    submit = SubmitField('Generate Schedule')

    def validate(self, **kwargs):
        if not super().validate(**kwargs): return False
        if not self.team.data and not self.team_member.data:
            msg = 'Either Team or Team Member must be selected.'
            self.team.errors.append(msg)
            self.team_member.errors.append(msg)
            return False
        return True

class ScheduleEntryFilterForm(FlaskForm):
    month_filter = StringField('Month (YYYY-MM)', validators=[Optional()])
    team = QuerySelectField('Team', query_factory=team_query, get_label='name', allow_blank=True, blank_text='-- All Teams --')
    team_member = QuerySelectField('Team Member', query_factory=team_member_query, get_label=get_member_label, allow_blank=True, blank_text='-- All Members --')
    submit = SubmitField('Filter')

# ==========================================
# ROUTE SHEET FORM (UPDATED)
# ==========================================
class RouteSheetForm(FlaskForm):
    ro_number = StringField('RO #', validators=[DataRequired(), Length(max=20)])
    customer_name = StringField('Customer Name', validators=[DataRequired(), Length(max=100)])
    vehicle_info = StringField('Vehicle', validators=[Optional(), Length(max=100)])

    asm = QuerySelectField('ASM', query_factory=asm_query, get_label='name', allow_blank=True, blank_text='-- ASM --')
    service_description = TextAreaField('Service / Repair', validators=[Optional(), Length(max=255)])

    # --- FIXED: Use get_member_label here to show Name + Number ---
    team_member = QuerySelectField('Tech', query_factory=team_member_query, get_label=get_member_label, allow_blank=True, blank_text='-- Tech --')
    # -------------------------------------------------------------

    status = SelectField('Status', choices=[
        ('Dispatch', 'To Dispatch'),
        ('Inspection', 'In Inspection'),
        ('Approval', 'Waiting Approval'),
        ('Parts', 'Parts Hold'),
        ('Service', 'In Service'),
        ('Warranty', 'Warranty / Wash'),
        ('Ready', 'Ready for Pickup'),
        ('Closed', 'Closed')
    ], default='Dispatch')

    promised_time = DateTimeLocalField('Promised Time', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    notes = TextAreaField('Internal Notes', validators=[Optional()])
    submit = SubmitField('Add RO')

# ==========================================
# WORK LOG & FINANCIAL FORMS
# ==========================================
class WorkLogForm(FlaskForm):
    team_member = QuerySelectField('Team Member', query_factory=team_member_query, get_label=get_member_label, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()], default=date.today)

    ro_number = StringField('RO Number', validators=[Optional(), Length(max=50)])
    line_item = StringField('Line Item', validators=[Optional(), Length(max=10)])
    flat_rate_hours = FloatField('Flat Rate Hours (Sold)', validators=[DataRequired(), NumberRange(min=0)])
    actual_time = FloatField('Actual Hours (Clocked)', validators=[Optional(), NumberRange(min=0)])

    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Work Log')

class QuickLogForm(FlaskForm):
    flat_rate_hours = FloatField('Hours', validators=[DataRequired(), NumberRange(min=0.1)])
    actual_time = FloatField('Actual Hours', validators=[Optional(), NumberRange(min=0)])
    notes = TextAreaField('Work Notes', validators=[Optional()])
    submit = SubmitField('Log Hours')

class FinancialPerformanceForm(FlaskForm):
    elr = DecimalField('Effective Labor Rate ($)', places=2, validators=[Optional(), NumberRange(min=0)])
    parts_to_labor_ratio = DecimalField('Parts-to-Labor Ratio', places=2, validators=[Optional(), NumberRange(min=0)])
    labor_margin = DecimalField('Labor Margin (%)', places=2, validators=[Optional(), NumberRange(min=0, max=100)])
    parts_margin = DecimalField('Parts Margin (%)', places=2, validators=[Optional(), NumberRange(min=0, max=100)])
    other_ro_gross = FloatField('Other RO Gross (+/- $)', validators=[Optional()])
    unapplied_time_cost = FloatField('Unapplied Time Cost ($)', validators=[Optional()])
    wholesale_gross = FloatField('Wholesale Gross (+/- $)', validators=[Optional()])
    parts_retail_gross = FloatField('Parts Retail Gross (+/- $)', validators=[Optional()])
    parts_inventory_adjust = FloatField('Parts Inventory Adjust (+/- $)', validators=[Optional()])
    parts_allowance = FloatField('Parts Allowance (+/- $)', validators=[Optional()])
    purchase_discounts = FloatField('Purchase Discounts (+/- $)', validators=[Optional()])
    submit = SubmitField('Update Financial Inputs')

class ReconciliationForm(FlaskForm):
    dms_file = FileField('Upload DMS Payroll/Flag Report (CSV)', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV Files Only!')
    ])
    submit = SubmitField('Run Audit')

# ==========================================
# LABOR MATRIX FORMS
# ==========================================
class LaborGridForm(FlaskForm):
    name = StringField('Grid Name', validators=[DataRequired(), Length(max=80)])
    description = StringField('Description (Optional)', validators=[Optional(), Length(max=200)])
    starting_rate = FloatField('Starting Rate ($/hr)', validators=[DataRequired(), NumberRange(min=0)])
    peak_hours = FloatField('Peak Hours (Hrs)', validators=[DataRequired(), NumberRange(min=0.1)])
    escalator_percent = FloatField('Escalator at Peak (%)', validators=[DataRequired()])
    return_normal_hours = FloatField('Return to Starting Rate (Hrs)', validators=[DataRequired(), NumberRange(min=0)])
    discount_start_hours = FloatField('Discount Starts After (Hrs)', validators=[Optional(), NumberRange(min=0)])
    discount_percent = FloatField('Discount Rate (% of Starting Rate)', validators=[Optional(), NumberRange(min=0, max=100)])
    submit = SubmitField('Save Grid and Calculate Rates')

    def validate_return_normal_hours(self, field):
        if self.peak_hours.data is not None and field.data is not None:
            if field.data <= self.peak_hours.data:
                raise ValidationError('Return Hours must be greater than Peak Hours.')

    def validate_discount_start_hours(self, field):
        if field.data is not None:
            if self.return_normal_hours.data is not None and field.data < self.return_normal_hours.data:
                raise ValidationError('Discount Start Hours must be greater than or equal to Return Hours.')
            if self.discount_percent.data is None:
                raise ValidationError('Discount Rate (%) must be provided if Discount Start Hours is set.')

    def validate_discount_percent(self, field):
        if field.data is not None:
            if self.discount_start_hours.data is None:
                raise ValidationError('Discount Start Hours must be provided if Discount Rate (%) is set.')

# ==========================================
# CALCULATOR FORMS
# ==========================================
class MPICalculatorForm(FlaskForm):
    effective_labor_rate = FloatField('Effective Labor Rate ($)', validators=[DataRequired()])
    tenths_increase = FloatField('Tenths Increase (e.g., 0.3)', default=0.3, validators=[DataRequired()])
    labor_gross_margin = FloatField('Labor Gross % (e.g., 0.75)', default=0.75, validators=[DataRequired()])
    parts_to_labor_ratio = FloatField('Parts to Labor Ratio', default=0.80, validators=[DataRequired()])
    parts_gross_margin = FloatField('Parts Gross % (e.g., 0.40)', default=0.40, validators=[DataRequired()])
    monthly_cp_ros = IntegerField('Monthly CP RO Count', validators=[DataRequired()])
    submit = SubmitField('Calculate Potential')

class ApptCalculatorForm(FlaskForm):
    num_techs = FloatField('Number of Techs', validators=[DataRequired()])
    proficiency = FloatField('Proficiency Target (e.g. 1.1)', default=1.1, validators=[DataRequired()])
    days_in_month = FloatField('Work Days in Month', default=21, validators=[DataRequired()])
    avg_hours_per_ro = FloatField('Avg Hours per RO (CP/WP)', default=2.0, validators=[DataRequired()])
    walk_in_percent = FloatField('Walk-in % (e.g. 0.10)', default=0.10, validators=[DataRequired()])
    show_rate = FloatField('Show Rate (e.g. 0.85)', default=0.85, validators=[DataRequired()])
    submit = SubmitField('Calculate Targets')

class CPGPOpportunityForm(FlaskForm):
    curr_elr = FloatField('Current ELR', validators=[DataRequired()])
    curr_hours_per_ro = FloatField('Current Hrs/RO', validators=[DataRequired()])
    curr_labor_margin = FloatField('Current Labor Margin %', validators=[DataRequired()])
    curr_parts_ratio = FloatField('Current P:L Ratio', validators=[DataRequired()])
    curr_parts_margin = FloatField('Current Parts Margin %', validators=[DataRequired()])
    curr_ro_count = IntegerField('Current Monthly ROs', validators=[DataRequired()])

    opp_elr = FloatField('Target ELR', validators=[DataRequired()])
    opp_hours_per_ro = FloatField('Target Hrs/RO', validators=[DataRequired()])
    opp_labor_margin = FloatField('Target Labor Margin %', validators=[DataRequired()])
    opp_parts_ratio = FloatField('Target P:L Ratio', validators=[DataRequired()])
    opp_parts_margin = FloatField('Target Parts Margin %', validators=[DataRequired()])
    opp_ro_count = IntegerField('Target Monthly ROs', validators=[DataRequired()])

    submit = SubmitField('Compare')

class CapacityOpportunityForm(FlaskForm):
    days_in_month = FloatField('Days in Month', default=21, validators=[DataRequired()])
    hours_per_day = FloatField('Hours per Day', default=8, validators=[DataRequired()])

    curr_tech_count = FloatField('Current Techs', validators=[DataRequired()])
    curr_proficiency = FloatField('Current Proficiency', validators=[DataRequired()])
    curr_elr = FloatField('Current ELR', validators=[DataRequired()])
    curr_labor_margin = FloatField('Current Labor Margin %', validators=[DataRequired()])
    curr_parts_ratio = FloatField('Current P:L Ratio', validators=[DataRequired()])
    curr_parts_margin = FloatField('Current Parts Margin %', validators=[DataRequired()])
    curr_unapplied = FloatField('Current Unapplied Cost ($)', default=0)

    opp_tech_count = FloatField('Target Techs', validators=[DataRequired()])
    opp_proficiency = FloatField('Target Proficiency', validators=[DataRequired()])
    opp_elr = FloatField('Target ELR', validators=[DataRequired()])
    opp_labor_margin = FloatField('Target Labor Margin %', validators=[DataRequired()])
    opp_parts_ratio = FloatField('Target P:L Ratio', validators=[DataRequired()])
    opp_parts_margin = FloatField('Target Parts Margin %', validators=[DataRequired()])
    opp_unapplied = FloatField('Target Unapplied Cost ($)', default=0)

    submit = SubmitField('Calculate Opportunity')

class PaceRecoveryCalculatorForm(FlaskForm):
    monthly_forecast_gross = FloatField(
        "Monthly Forecast Gross",
        validators=[DataRequired(), NumberRange(min=0)],
    )
    mtd_actual_gross = FloatField(
        "MTD Actual Gross",
        validators=[DataRequired(), NumberRange(min=0)],
    )
    monthly_frh_goal = FloatField(
        "Monthly FRH Goal",
        validators=[DataRequired(), NumberRange(min=0)],
    )
    mtd_actual_frh = FloatField(
        "MTD Actual FRH",
        validators=[DataRequired(), NumberRange(min=0)],
    )
    elapsed_workdays = FloatField(
        "Elapsed Workdays",
        validators=[DataRequired(), NumberRange(min=0.1)],
    )
    remaining_workdays = FloatField(
        "Remaining Workdays",
        validators=[DataRequired(), NumberRange(min=0.1)],
    )
    avg_hours_per_ro = FloatField(
        "Average Hours per RO",
        validators=[DataRequired(), NumberRange(min=0.1)],
    )
    avg_gross_per_ro = FloatField(
        "Average Gross per RO",
        validators=[DataRequired(), NumberRange(min=0.1)],
    )
    submit = SubmitField("Calculate Recovery Plan")


class AppointmentLiftCalculatorForm(FlaskForm):
    additional_appointments = IntegerField(
        "Additional Appointments",
        validators=[DataRequired(), NumberRange(min=0)],
    )
    avg_hours_per_ro = FloatField(
        "Average Hours per RO",
        validators=[DataRequired(), NumberRange(min=0.1)],
    )
    avg_gross_per_ro = FloatField(
        "Average Gross per RO",
        validators=[DataRequired(), NumberRange(min=0.1)],
    )
    show_rate = FloatField(
        "Show Rate (%)",
        validators=[DataRequired(), NumberRange(min=0, max=100)],
    )
    workdays_per_month = FloatField(
        "Workdays per Month",
        validators=[DataRequired(), NumberRange(min=0.1)],
    )
    submit = SubmitField("Calculate Appointment Lift")    

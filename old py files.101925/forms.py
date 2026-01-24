from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField, SelectField,
    FloatField, SelectMultipleField, DateField, TimeField, TextAreaField,
    DecimalField
)
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, NumberRange, Optional
from wtforms.widgets import CheckboxInput, ListWidget, NumberInput
from wtforms_sqlalchemy.fields import QuerySelectField
from datetime import date, time, timedelta
import calendar
from extensions import db
from models import User, Team, TeamMember
from flask import request
from dateutil.relativedelta import relativedelta

# --- Query Functions ---

def team_query():
    return Team.query.order_by(Team.name)

def team_member_query():
    return TeamMember.query.order_by(TeamMember.name)

def get_month_choices(months_back=12):
    # Generates a list of (YYYY-MM, MonthName YYYY) tuples for the last 12 months (or more)
    today = date.today()
    choices = []
    
    for i in range(months_back):
        # Calculate the target date (i months ago from the 1st of the current month)
        target_date = today.replace(day=1) - relativedelta(months=i)
        
        # Value is YYYY-MM for parsing in the route
        value = target_date.strftime('%Y-%m')
        
        # Label is Month Name YYYY
        label = target_date.strftime('%B %Y')
        
        choices.append((value, label))
    
    return choices

# --- Schedule Entry Filter Form (FIXED) ---

class ScheduleEntryFilterForm(FlaskForm):
    # CRITICAL FIX: Combined the two definitions to include both filters
    team = QuerySelectField(
        'Filter by Team',
        query_factory=team_query,
        get_pk=lambda a: a.id,
        get_label=lambda a: a.name,
        allow_blank=True,
        blank_text='All Teams'
    )
    
    team_member = QuerySelectField(
        'Filter by Team Member', 
        query_factory=team_member_query, 
        get_label='name', 
        allow_blank=True, 
        blank_text='-- All Team Members --'
    )

# NEW FIELD: Month Selector
    month_filter = SelectField(
        'Select Month', 
        choices=get_month_choices(),
        validators=[Optional()] # Optional so it can be omitted if not needed
    )
   
    submit = SubmitField('Filter')

# --- Other Helper Functions (retained) ---
def get_teams():
    # This function isn't used by the new filter form but is kept for compatibility
    return Team.query.all()

# --- Authentication Forms ---

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
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

# --- Team and Team Member Forms ---

class TeamForm(FlaskForm):
    name = StringField('Team Name', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Save Team')
    original_team_id = None

    def validate_name(self, name):
        if self.original_team_id:
            existing_team = Team.query.filter_by(name=name.data).first()
            if existing_team and existing_team.id != self.original_team_id:
                raise ValidationError('A team with that name already exists. Please choose a different one.')
        else:
            existing_team = Team.query.filter_by(name=name.data).first()
            if existing_team:
                raise ValidationError('A team with that name already exists. Please choose a different one.')


class TeamMemberForm(FlaskForm):
    name = StringField('Member Name', validators=[DataRequired(), Length(min=2, max=50)])
    team = QuerySelectField('Team', query_factory=team_query, get_label='name', validators=[DataRequired()])
    tech_level = SelectField('Tech Level', choices=[
        ('', 'Select...'), ('Level 1', 'Level 1'), ('Level 2', 'Level 2'),
        ('Level 3', 'Level 3'), ('Master Tech', 'Master Tech')
    ], validators=[DataRequired()])
    daily_production_objective = FloatField('Daily Production Objective (hrs)', validators=[
        NumberRange(min=0, message='Must be a positive number or zero.')
    ])
    submit = SubmitField('Save Member')
    
# --- Schedule Forms ---

class ScheduleEntryForm(FlaskForm):
    team_member = QuerySelectField('Team Member', query_factory=team_member_query, get_label='name', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    lunch_start = TimeField('Lunch Start')
    lunch_end = TimeField('Lunch End')
    notes = StringField('Notes')
    submit = SubmitField('Save Schedule Entry')


class TeamScheduleForm(FlaskForm):
    team = QuerySelectField('Team', query_factory=team_query, get_label='name', validators=[DataRequired()])
    day_of_week = SelectField('Day of Week', choices=[
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'),
        (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ], coerce=int, validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    lunch_start = TimeField('Lunch Start')
    lunch_end = TimeField('Lunch End')
    notes = StringField('Notes')
    submit = SubmitField('Save Recurring Schedule')


class RecurringScheduleForm(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    
    days_of_week = SelectMultipleField(
        'Days of Week',
        choices=[
            (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
            (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
        ],
        option_widget=CheckboxInput(),
        widget=ListWidget(prefix_label=False),
        coerce=int
    )
    
    team = QuerySelectField(
        'Team',
        query_factory=team_query,
        get_label='name',
        allow_blank=True,
        blank_text='Select a Team'
    )
    team_member = QuerySelectField(
        'Team Member',
        query_factory=team_member_query,
        get_label='name',
        allow_blank=True,
        blank_text='No override (Schedule Team)'
    )

    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    lunch_start = TimeField('Lunch Start', validators=[Optional()])
    lunch_end = TimeField('Lunch End', validators=[Optional()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Generate Schedules')

    def validate_team_selection(self):
        # Custom validation to ensure either team or team_member is selected, but not both
        if not self.team.data and not self.team_member.data:
            self.team_member.errors.append("You must select either a team or a team member.")
            return False
        
        if self.team.data and self.team_member.data:
            self.team_member.errors.append("You cannot select both a team and a team member. The team member field is for overrides only.")
            return False
        
        return True

# --- Work Log Form ---

class WorkLogForm(FlaskForm):
    team_member = QuerySelectField('Team Member', query_factory=team_member_query, get_label='name', validators=[DataRequired()])
    date = DateField('Date', default=date.today, validators=[DataRequired()])
    start_time = TimeField('Start Time', default=time(8, 0), validators=[DataRequired()])
    end_time = TimeField('End Time', default=time(17, 0), validators=[DataRequired()])
    ro_number = StringField('Repair Order Number')
    line_item = StringField('Line Item')
    
    flat_rate_hours = DecimalField(
        'Flat Rate Hours', 
        validators=[DataRequired(), NumberRange(min=0.01, message='Hours must be greater than zero.')],
        widget=NumberInput(step='0.01') # Ensure the input allows decimals
    )
    
    notes = StringField('Notes')
    submit = SubmitField('Save Work Log')

# --- Financial Performance Form ---

class FinancialPerformanceForm(FlaskForm):
    # --- Currency Fields ($) ---
    elr = DecimalField('Effective Labor Rate ($/hr)',
                       default=0.0,
                       validators=[DataRequired(), NumberRange(min=0)],
                       widget=NumberInput(step='0.01'), 
                       render_kw={"placeholder": "$"})
                       
    # --- Percentage Fields (%) ---
    parts_to_labor_ratio = DecimalField('Parts to Labor Ratio (%)',
                                        default=0.0,
                                        validators=[DataRequired(), NumberRange(min=0)],
                                        widget=NumberInput(step='0.01'),
                                        render_kw={"placeholder": "%"})
                                        
    labor_margin = DecimalField('Labor Margin (%)',
                                default=0.0,
                                validators=[DataRequired(), NumberRange(min=0, max=100)], 
                                widget=NumberInput(step='0.01'),
                                render_kw={"placeholder": "%"})
                                        
    parts_margin = DecimalField('Parts Margin (%)',
                                default=0.0,
                                validators=[DataRequired(), NumberRange(min=0, max=100)], 
                                widget=NumberInput(step='0.01'),
                                render_kw={"placeholder": "%"})
                                        
    # --- Adjustment Fields (Currency $) ---
    other_ro_gross = DecimalField('Other RO Gross ($)', 
                                  default=0.0, 
                                  validators=[NumberRange(min=-10000000.0, max=10000000.0)],
                                  widget=NumberInput(step='0.01'),
                                  render_kw={"placeholder": "$"})
                                  
    unapplied_time_cost = DecimalField('Unapplied Time Cost ($)', 
                                        default=0.0, 
                                        validators=[NumberRange(min=-10000000.0, max=10000000.0)],
                                        widget=NumberInput(step='0.01'),
                                        render_kw={"placeholder": "$"})
                                        
    parts_inventory_adjust = DecimalField('Parts Inventory Adjust ($)', 
                                            default=0.0, 
                                            validators=[NumberRange(min=-10000000.0, max=10000000.0)],
                                            widget=NumberInput(step='0.01'),
                                            render_kw={"placeholder": "$"})
                                            
    parts_allowance = DecimalField('Parts Allowance ($)', 
                                    default=0.0, 
                                    validators=[NumberRange(min=-10000000.0, max=10000000.0)],
                                    widget=NumberInput(step='0.01'),
                                    render_kw={"placeholder": "$"})
                                    
    purchase_discounts = DecimalField('Purchase Discounts ($)', 
                                        default=0.0, 
                                        validators=[NumberRange(min=-10000000.0, max=10000000.0)],
                                        widget=NumberInput(step='0.01'),
                                        render_kw={"placeholder": "$"})
                                        
    wholesale_gross = DecimalField('Wholesale Gross ($)', 
                                   default=0.0, 
                                   validators=[NumberRange(min=-10000000.0, max=10000000.0)],
                                   widget=NumberInput(step='0.01'),
                                   render_kw={"placeholder": "$"})
                                   
    parts_retail_gross = DecimalField('Parts Retail Gross ($)', 
                                      default=0.0, 
                                      validators=[NumberRange(min=-10000000.0, max=10000000.0)],
                                      widget=NumberInput(step='0.01'),
                                      render_kw={"placeholder": "$"})
                                      
    submit_finance = SubmitField('Calculate Financials')

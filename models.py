from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date, time
from extensions import db 
from sqlalchemy.orm import relationship
import secrets

# ===================================================================
# ONBOARDING & AUTH MODELS
# ===================================================================
class OnboardingTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), nullable=False) 
    store_name_placeholder = db.Column(db.String(100), nullable=True)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, email, store_name=None):
        self.email = email
        self.store_name_placeholder = store_name
        self.token = secrets.token_urlsafe(32)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    store_id = db.Column(db.Integer, nullable=False, default=1)
    
    financial_inputs = db.relationship('FinancialInputs', backref='user', uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"User('{self.username}')"

# ===================================================================
# FINANCIAL MODELS
# ===================================================================
class FinancialInputs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    
    effective_labor_rate = db.Column(db.Float, nullable=True) 
    parts_to_labor_ratio = db.Column(db.Float, nullable=True)
    labor_margin = db.Column(db.Float, nullable=True)
    parts_margin = db.Column(db.Float, nullable=True)
    
    cp_effective_labor_rate = db.Column(db.Float, nullable=True)
    cp_parts_to_labor_ratio = db.Column(db.Float, nullable=True)
    cp_labor_margin = db.Column(db.Float, nullable=True)
    cp_parts_margin = db.Column(db.Float, nullable=True)
    
    other_ro_gross = db.Column(db.Float, nullable=True)
    unapplied_time_cost = db.Column(db.Float, nullable=True) 
    parts_retail_gross = db.Column(db.Float, nullable=True)
    wholesale_gross = db.Column(db.Float, nullable=True)
    parts_inventory_adjust = db.Column(db.Float, nullable=True)
    parts_allowance = db.Column(db.Float, nullable=True)
    purchase_discounts = db.Column(db.Float, nullable=True)
    
    parts_fill_rate = db.Column(db.Float, nullable=True)
    parts_turn_rate = db.Column(db.Float, nullable=True)
    
    bays_with_lifts = db.Column(db.Integer, nullable=True)
    bays_without_lifts = db.Column(db.Integer, nullable=True)

class FinancialForecast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    store_id = db.Column(db.Integer, nullable=False, default=1)
    
    labor_gross = db.Column(db.Float, nullable=False, default=0.0)
    parts_gross = db.Column(db.Float, nullable=False, default=0.0)
    other_gross = db.Column(db.Float, nullable=True, default=0.0)
    total_gross = db.Column(db.Float, nullable=False, default=0.0)
    expected_frh = db.Column(db.Float, nullable=False, default=0.0)
    date_updated = db.Column(db.Date, nullable=False, default=date.today)

# ===================================================================
# TEAM & STAFF MODELS
# ===================================================================
class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    store_id = db.Column(db.Integer, nullable=False, default=1)
    
    members = db.relationship('TeamMember', backref='team', lazy=True, cascade="all, delete-orphan")
    asms = db.relationship('ASM', backref='team', lazy=True, cascade="all, delete-orphan") 
    schedules = db.relationship('TeamSchedule', backref='team', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Team('{self.name}')"

class ASM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    asm_number = db.Column(db.String(20), nullable=True)
    store_id = db.Column(db.Integer, nullable=False, default=1)
    
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    repair_orders = db.relationship('RepairOrder', backref='asm', lazy=True)

    def __repr__(self):
        return f"ASM('{self.name}', '{self.asm_number}')"

class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tech_number = db.Column(db.String(20), nullable=True) 
    tech_level = db.Column(db.String(50), nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    
    daily_production_objective = db.Column(db.Float, nullable=True, default=8.0)
    dpo_calculation_mode = db.Column(db.String(20), nullable=False, default='manual') 
    hist_frh_total = db.Column(db.Float, nullable=True, default=80.0)
    hist_days_in_period = db.Column(db.Integer, nullable=True, default=10)
    hist_training_days = db.Column(db.Integer, nullable=True, default=0)
    hist_vacation_days = db.Column(db.Integer, nullable=True, default=0)
    expected_lift_percent = db.Column(db.Float, nullable=True, default=100.0) 

    schedule_entries = db.relationship('ScheduleEntry', backref='team_member', lazy=True, cascade="all, delete-orphan")
    work_logs = db.relationship('WorkLog', backref='team_member', lazy=True, cascade="all, delete-orphan")
    memos = db.relationship('ProductionObjectiveMemo', backref='team_member', lazy=True, cascade="all, delete-orphan")
    
    # --- THIS IS THE MISSING LINK ---
    repair_orders = db.relationship('RepairOrder', backref='team_member', lazy=True)
    # --------------------------------

    def __repr__(self):
        return f"TeamMember('{self.name}', Tech#{self.tech_number})"

    @property
    def calculated_dpo(self):
        try:
            frh = self.hist_frh_total or 0.0
            total_days = self.hist_days_in_period or 1
            train_days = self.hist_training_days or 0
            vac_days = self.hist_vacation_days or 0
            lift = (self.expected_lift_percent or 100.0) / 100.0
            actual_days_worked = total_days - train_days - vac_days
            if actual_days_worked <= 0: return 0.0
            baseline_dpo = frh / actual_days_worked
            final_dpo = baseline_dpo * lift
            return final_dpo
        except Exception:
            return 0.0

class ProductionObjectiveMemo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_member_id = db.Column(db.Integer, db.ForeignKey('team_member.id'), nullable=False)
    previous_objective = db.Column(db.Float, nullable=True)
    change_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# ===================================================================
# SCHEDULE & WORKFLOW MODELS
# ===================================================================
class ScheduleEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_member_id = db.Column(db.Integer, db.ForeignKey('team_member.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    lunch_start = db.Column(db.Time, nullable=True)
    lunch_end = db.Column(db.Time, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    schedule_type = db.Column(db.String(20), nullable=False, default='WORK')

class TeamSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    lunch_start = db.Column(db.Time, nullable=True)
    lunch_end = db.Column(db.Time, nullable=True)
    notes = db.Column(db.Text, nullable=True)

class WorkLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_member_id = db.Column(db.Integer, db.ForeignKey('team_member.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    # No start/end times as per recent update request
    actual_time = db.Column(db.Float, nullable=True) # Actual clock hours
    ro_number = db.Column(db.String(50), nullable=True)
    line_item = db.Column(db.String(10), nullable=True)
    flat_rate_hours = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text, nullable=True)

class RepairOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ro_number = db.Column(db.String(20), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    vehicle_info = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(50), nullable=False, default='Dispatch')
    promised_time = db.Column(db.DateTime, nullable=True)
    service_description = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    notes_read = db.Column(db.Boolean, default=False) # Track if notes viewed
    
    store_id = db.Column(db.Integer, nullable=False, default=1)
    team_member_id = db.Column(db.Integer, db.ForeignKey('team_member.id'), nullable=True)
    asm_id = db.Column(db.Integer, db.ForeignKey('asm.id'), nullable=True)
    advisor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"RO('{self.ro_number}', '{self.status}')"

class Holiday(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    month_day = db.Column(db.String(5), unique=True, nullable=False) 

    def __repr__(self):
        return f"Holiday('{self.name}', '{self.month_day}')"

# ===================================================================
# LABOR GRID MODELS
# ===================================================================
class LaborGrid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean, default=False, nullable=False)
    
    starting_rate = db.Column(db.Float, nullable=False, default=100.0)
    peak_hours = db.Column(db.Float, nullable=False, default=2.0)
    escalator_percent = db.Column(db.Float, nullable=False, default=10.0)
    return_normal_hours = db.Column(db.Float, nullable=False, default=5.0)
    discount_start_hours = db.Column(db.Float, nullable=True)
    discount_percent = db.Column(db.Float, nullable=True)
    
    rates = db.relationship('LaborGridRate', backref='grid', lazy=True, cascade="all, delete-orphan")

class LaborGridRate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hours = db.Column(db.Float, nullable=False)
    effective_rate = db.Column(db.Float, nullable=False)
    grid_id = db.Column(db.Integer, db.ForeignKey('labor_grid.id'), nullable=False)
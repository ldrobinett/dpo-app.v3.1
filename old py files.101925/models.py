# 01.prodapp.0825/models.py

from extensions import db
from flask_login import UserMixin
from datetime import datetime, date
from sqlalchemy.types import TypeDecorator, String
from sqlalchemy import Numeric
import json # Import for handling the days_of_week list

# --- Custom Type for List of Integers (Days of Week) ---
# Allows storing a list of ints (e.g., [0, 1, 2]) as a string in SQLite
class JSONEncodedDict(TypeDecorator):
    """Enables proper storage of json-ified dict/list to string columns."""
    impl = String
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value

# --- Existing Models ---

class ProductionObjectiveMemo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_member_id = db.Column(db.Integer, db.ForeignKey('team_member.id'), nullable=False)
    previous_objective = db.Column(db.Float, nullable=False)
    change_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    team_member = db.relationship('TeamMember', backref=db.backref('memos', lazy=True))

    def __repr__(self):
        return f"Memo(ID: {self.id}, Previous Objective: {self.previous_objective})"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    members = db.relationship('TeamMember', backref='team', lazy=True)
    team_schedules = db.relationship('TeamSchedule', backref='team', lazy=True)

class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    tech_level = db.Column(db.String(20), nullable=True)
    daily_production_objective = db.Column(db.Float, nullable=True)
    
class ScheduleEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_member_id = db.Column(db.Integer, db.ForeignKey('team_member.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    lunch_start = db.Column(db.Time, nullable=True)
    lunch_end = db.Column(db.Time, nullable=True)
    notes = db.Column(db.String(200), nullable=True)
    team_member = db.relationship('TeamMember', backref=db.backref('schedule_entries', lazy=True), foreign_keys=[team_member_id])

class WorkLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_member_id = db.Column(db.Integer, db.ForeignKey('team_member.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    ro_number = db.Column(db.String(50), nullable=True)
    line_item = db.Column(db.String(200), nullable=True)
    flat_rate_hours = db.Column(db.Numeric(precision=10, scale=2), nullable=False, default=0.0) 
    notes = db.Column(db.String(200), nullable=True)
    team_member = db.relationship('TeamMember', backref=db.backref('work_logs', lazy=True), foreign_keys=[team_member_id])

class TeamSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    lunch_start = db.Column(db.Time, nullable=True)
    lunch_end = db.Column(db.Time, nullable=True)
    notes = db.Column(db.String(200), nullable=True)


# --- NEW MODEL: RecurringSchedule ---
class RecurringSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Dates for the range
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    # Days of the week (Stored as a JSON list of integers)
    days_of_week = db.Column(JSONEncodedDict(50), nullable=False) 
    
    # Time details
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    lunch_start = db.Column(db.Time, nullable=True)
    lunch_end = db.Column(db.Time, nullable=True)
    
    # Associated Team/TeamMember (Foreign Keys) - Nullable because one MUST be selected
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    team_member_id = db.Column(db.Integer, db.ForeignKey('team_member.id'), nullable=True)
    
    # Relationships
    team = db.relationship('Team', backref='recurring_schedules', foreign_keys=[team_id])
    team_member = db.relationship('TeamMember', backref='recurring_schedules', foreign_keys=[team_member_id])
    
    notes = db.Column(db.String(200), nullable=True)
    # Assuming user association is needed
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Assuming nullable for now

    def __repr__(self):
        return f"RecurringSchedule(ID: {self.id}, Team/Member: {self.team_id or self.team_member_id})"


# --- Existing Models Continued ---

class FinancialForecast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    labor_gross = db.Column(db.Float, nullable=False)
    parts_gross = db.Column(db.Float, nullable=False)
    total_gross = db.Column(db.Float, nullable=False)
    expected_frh = db.Column(db.Float, nullable=False)
    date_updated = db.Column(db.Date, nullable=False, default=date.today)

class FinancialInputs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    effective_labor_rate = db.Column(db.Float, default=0.0)
    parts_to_labor_ratio = db.Column(db.Float, default=0.0)
    labor_margin = db.Column(db.Float, default=0.0)
    parts_margin = db.Column(db.Float, default=0.0)
    other_ro_gross = db.Column(db.Float, default=0.0)
    unapplied_time_cost = db.Column(db.Float, default=0.0) # Represents the dollar cost of unapplied time
    parts_inventory_adjust = db.Column(db.Float, default=0.0)
    parts_allowance = db.Column(db.Float, default=0.0)
    purchase_discounts = db.Column(db.Float, default=0.0)
    wholesale_gross = db.Column(db.Float, default=0.0)
    parts_retail_gross = db.Column(db.Float, default=0.0)

    def __repr__(self):
        # Corrected __repr__ since this model doesn't have month/year
        return f"FinancialInputs(User ID: {self.user_id})"

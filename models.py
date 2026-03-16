from flask_login import UserMixin
from datetime import datetime, date, time
from extensions import db
from sqlalchemy.orm import relationship
import secrets
from cryptography.fernet import Fernet, InvalidToken
import base64
import hashlib
from security import get_fernet


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


# ===================================================================
# ROLE & CAPABILITY MODELS
# ===================================================================

user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id"), primary_key=True),
)

role_capabilities = db.Table(
    "role_capabilities",
    db.Column("role_id", db.Integer, db.ForeignKey("role.id"), primary_key=True),
    db.Column("capability_id", db.Integer, db.ForeignKey("capability.id"), primary_key=True),
)


class Capability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"<Capability {self.key}>"


class Role(db.Model):
    __tablename__ = "role"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    store_id = db.Column(
        db.Integer,
        db.ForeignKey("managed_store.id"),
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint(
            "store_id",
            "name",
            name="uq_role_store_name"
        ),
        db.Index("ix_role_store_id", "store_id"),
    )
    capabilities = db.relationship(
        "Capability",
        secondary=role_capabilities,
        backref="roles",
        lazy="subquery"
    )
    def __repr__(self):
        return f"<Role {self.name}>"


# ===================================================================
# USERS
# ===================================================================

class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    store_id = db.Column(
        db.Integer,
        db.ForeignKey("managed_store.id"),
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint("store_id", "username", name="uq_user_store_username"),
        db.Index("ix_user_store_id", "store_id"),
    )
    roles = db.relationship(
        "Role",
        secondary=user_roles,
        backref="users",
        lazy="subquery"
    )

    financial_inputs = db.relationship(
        "FinancialInputs",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def get_id(self):
        return f"u:{self.id}"

    @property
    def is_operator(self) -> bool:
        return False

    def __repr__(self):
        return f"User('{self.username}')"


class OperatorUser(db.Model, UserMixin):
    __tablename__ = "operator_user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def get_id(self):
        return f"op:{self.id}"

    def check_password(self, bcrypt, candidate: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, candidate)

    @property
    def is_operator(self) -> bool:
        return True


# ===================================================================
# OPERATOR / STORE MODELS
# ===================================================================

class ManagedStore(db.Model):
    __tablename__ = "managed_store"

    id = db.Column(db.Integer, primary_key=True)  # ✅ REQUIRED

    name = db.Column(db.String(120), nullable=False)
    environment = db.Column(db.String(16), nullable=False, default="prod")  # dev/staging/prod
    tier = db.Column(db.String(20), nullable=False, server_default="beta")         # ✅ matches template
    status = db.Column(db.String(16), nullable=False, default="active")     # active/archived/deleted

    url = db.Column(db.String(255), nullable=False)

    admin_username = db.Column(db.String(120), nullable=False)
    admin_password_enc = db.Column(db.LargeBinary, nullable=True)  # ✅ single source of truth

    notes = db.Column(db.Text, nullable=True)

    archived_at = db.Column(db.DateTime, nullable=True)
    deleted_at  = db.Column(db.DateTime, nullable=True)

    deleted_by_operator_id = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    routesheet_audit_timestamp = db.Column(db.DateTime)
    tech_hours_audit_timestamp = db.Column(db.DateTime)

    @property
    def is_active(self) -> bool:
        return self.status == "active"

    @property
    def is_archived(self) -> bool:
        return self.status == "archived"

    @property
    def is_deleted(self) -> bool:
        return self.status == "deleted"

    def set_admin_password(self, plaintext: str):
        f = get_fernet()
        self.admin_password_enc = f.encrypt(plaintext.encode("utf-8"))

    def get_admin_password(self) -> str:
        if not self.admin_password_enc:
            return ""
        f = get_fernet()
        return f.decrypt(self.admin_password_enc).decode("utf-8")



class Store(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    base_url = db.Column(db.String(255), nullable=False)

    admin_username = db.Column(db.String(80), nullable=False)
    admin_password_hash = db.Column(db.String(255), nullable=False)

    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Lifecycle tracking (NEW)
    archived_at = db.Column(db.DateTime, nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


# ===================================================================
# FINANCIAL MODELS
# ===================================================================

class FinancialInputs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)

    effective_labor_rate = db.Column(db.Float)
    parts_to_labor_ratio = db.Column(db.Float)
    labor_margin = db.Column(db.Float)
    parts_margin = db.Column(db.Float)

    cp_effective_labor_rate = db.Column(db.Float)
    cp_parts_to_labor_ratio = db.Column(db.Float)
    cp_labor_margin = db.Column(db.Float)
    cp_parts_margin = db.Column(db.Float)

    other_ro_gross = db.Column(db.Float)
    unapplied_time_cost = db.Column(db.Float)
    parts_retail_gross = db.Column(db.Float)
    wholesale_gross = db.Column(db.Float)
    parts_inventory_adjust = db.Column(db.Float)
    parts_allowance = db.Column(db.Float)
    purchase_discounts = db.Column(db.Float)

    parts_fill_rate = db.Column(db.Float)
    parts_turn_rate = db.Column(db.Float)

    bays_with_lifts = db.Column(db.Integer)
    bays_without_lifts = db.Column(db.Integer)


class FinancialForecast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    store_id = db.Column(
        db.Integer,
        db.ForeignKey("managed_store.id"),
        nullable=False
    )

    __table_args__ = (db.Index("ix_forecast_store_id", "store_id"),)

    labor_gross = db.Column(db.Float, default=0.0)
    parts_gross = db.Column(db.Float, default=0.0)
    other_gross = db.Column(db.Float, default=0.0)
    total_gross = db.Column(db.Float, default=0.0)
    expected_frh = db.Column(db.Float, default=0.0)
    date_updated = db.Column(db.Date, default=date.today)


# ===================================================================
# TEAM & STAFF MODELS
# ===================================================================

class Team(db.Model):
    __tablename__ = "team"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    store_id = db.Column(
        db.Integer,
        db.ForeignKey("managed_store.id"),
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint(
            "store_id",
            "name",
            name="uq_team_store_name"
        ),
        db.Index("ix_team_store_id", "store_id"),
    )


    members = db.relationship("TeamMember", backref="team", lazy=True, cascade="all, delete-orphan")
    asms = db.relationship("ASM", backref="team", lazy=True, cascade="all, delete-orphan")
    schedules = db.relationship("TeamSchedule", backref="team", lazy=True, cascade="all, delete-orphan")


class ASM(db.Model):
    __tablename__ = "asm"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    asm_number = db.Column(db.String(20), nullable=True)
    store_id = db.Column(
        db.Integer,
        db.ForeignKey("managed_store.id"),
        nullable=False
    )

    team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=False)
    repair_orders = db.relationship("RepairOrder", backref="asm", lazy=True)

    __table_args__ = (
        db.UniqueConstraint("store_id", "asm_number", name="uq_asm_store_number"),
        db.Index("ix_asm_store_id", "store_id"),
    )

class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tech_number = db.Column(db.String(20))
    tech_level = db.Column(db.String(50))
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"))

    daily_production_objective = db.Column(db.Float, default=8.0)
    dpo_calculation_mode = db.Column(db.String(20), default="manual")
    hist_frh_total = db.Column(db.Float, default=80.0)
    hist_days_in_period = db.Column(db.Integer, default=10)
    hist_training_days = db.Column(db.Integer, default=0)
    hist_vacation_days = db.Column(db.Integer, default=0)
    expected_lift_percent = db.Column(db.Float, default=100.0)

    schedule_entries = db.relationship("ScheduleEntry", backref="team_member", lazy=True, cascade="all, delete-orphan")
    work_logs = db.relationship("WorkLog", backref="team_member", lazy=True, cascade="all, delete-orphan")
    repair_orders = db.relationship("RepairOrder", backref="team_member", lazy=True)

    # ✅ ADD THIS (finance imports it / you use it for DPO history)
    memos = db.relationship(
        "ProductionObjectiveMemo",
        backref="team_member",
        lazy=True,
        cascade="all, delete-orphan"
    )

    @property
    def calculated_dpo(self):
        try:
            frh = self.hist_frh_total or 0.0
            days = (self.hist_days_in_period or 1) - (self.hist_training_days or 0) - (self.hist_vacation_days or 0)
            if days <= 0:
                return 0.0
            return (frh / days) * ((self.expected_lift_percent or 100) / 100)
        except Exception:
            return 0.0


# ✅ ADD THIS CLASS (this is what your import error is about)
class ProductionObjectiveMemo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_member_id = db.Column(db.Integer, db.ForeignKey("team_member.id"), nullable=False)
    previous_objective = db.Column(db.Float)
    change_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<ProductionObjectiveMemo member_id={self.team_member_id}>"


# ===================================================================
# SCHEDULE & WORKFLOW MODELS
# ===================================================================

class ScheduleEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_member_id = db.Column(db.Integer, db.ForeignKey("team_member.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    lunch_start = db.Column(db.Time)
    lunch_end = db.Column(db.Time)
    notes = db.Column(db.Text)
    schedule_type = db.Column(db.String(20), default="WORK")


class TeamSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    lunch_start = db.Column(db.Time)
    lunch_end = db.Column(db.Time)
    notes = db.Column(db.Text)


class WorkLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_member_id = db.Column(db.Integer, db.ForeignKey("team_member.id"), nullable=False)
    date = db.Column(db.Date, default=date.today)
    actual_time = db.Column(db.Float)
    ro_number = db.Column(db.String(50))
    line_item = db.Column(db.String(10))
    flat_rate_hours = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)


class RepairOrder(db.Model):
    __tablename__ = "repair_order"

    id = db.Column(db.Integer, primary_key=True)
    ro_number = db.Column(db.String(20), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    vehicle_info = db.Column(db.String(100))
    status = db.Column(db.String(50), default="Dispatch")
    promised_time = db.Column(db.DateTime)
    service_description = db.Column(db.Text)
    notes = db.Column(db.Text)
    notes_read = db.Column(db.Boolean, default=False)

    store_id = db.Column(
        db.Integer,
        db.ForeignKey("managed_store.id"),
        nullable=False
    )
    team_member_id = db.Column(db.Integer, db.ForeignKey("team_member.id"))
    asm_id = db.Column(db.Integer, db.ForeignKey("asm.id"))
    advisor_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("store_id", "ro_number", name="uq_ro_store_number"),
        db.Index("ix_ro_store_id", "store_id"),
    )

    audited = db.Column(db.Boolean, default=False)
    audit_source = db.Column(db.String(50))  # "CDK"
    audit_timestamp = db.Column(db.DateTime)

class Holiday(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    month_day = db.Column(db.String(5), unique=True, nullable=False)


# ===================================================================
# LABOR GRID MODELS
# ===================================================================

class LaborGrid(db.Model):
    __tablename__ = "labor_grid"

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(
        db.Integer,
        db.ForeignKey("managed_store.id"),
        nullable=False
    )
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=False)

    __table_args__ = (
        db.UniqueConstraint("store_id", "name", name="uq_laborgrid_store_name"),
        db.Index("ix_laborgrid_store_id", "store_id"),
    )

    starting_rate = db.Column(db.Float, default=100.0)
    peak_hours = db.Column(db.Float, default=2.0)
    escalator_percent = db.Column(db.Float, default=10.0)
    return_normal_hours = db.Column(db.Float, default=5.0)
    discount_start_hours = db.Column(db.Float)
    discount_percent = db.Column(db.Float)

    rates = db.relationship("LaborGridRate", backref="grid", lazy=True, cascade="all, delete-orphan")


class LaborGridRate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hours = db.Column(db.Float, nullable=False)
    effective_rate = db.Column(db.Float, nullable=False)
    grid_id = db.Column(db.Integer, db.ForeignKey("labor_grid.id"), nullable=False)

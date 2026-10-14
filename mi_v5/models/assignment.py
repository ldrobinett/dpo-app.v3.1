"""Canonical effective-dated Employee/Role accountability in a Department."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, ForeignKeyConstraint, Index,
    String, UniqueConstraint, event, inspect, text,
)
from sqlalchemy.orm import Mapped, mapped_column, validates

from mi_v5.database.entities import TenantEntity
from mi_v5.database.types import UUID_TYPE


class Assignment(TenantEntity):
    """One canonical Role assignment; Position occupancy remains separate."""

    __tablename__ = "assignments"
    __id_column_name__ = "assignment_id"

    employee_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    role_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    department_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    effective_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    effective_to: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, active_history=True
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False)
    source_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["enterprise_id", "employee_id"],
            ["employees.enterprise_id", "employees.employee_id"],
            name="fk_assignments_employee", ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "role_id"],
            ["roles.enterprise_id", "roles.role_id"],
            name="fk_assignments_role", ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "department_id"],
            ["departments.enterprise_id", "departments.department_id"],
            name="fk_assignments_department", ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "created_by_id"],
            ["employees.enterprise_id", "employees.employee_id"],
            name="fk_assignments_created_by", ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "updated_by_id"],
            ["employees.enterprise_id", "employees.employee_id"],
            name="fk_assignments_updated_by", ondelete="RESTRICT",
        ),
        CheckConstraint(
            "effective_to IS NULL OR effective_to > effective_from",
            name="effective_period_valid",
        ),
        CheckConstraint(
            "status IN ('pending', 'active', 'completed', 'cancelled')",
            name="status_valid",
        ),
        CheckConstraint(
            "status != 'active' OR (created_by_id IS NOT NULL "
            "AND source_reference IS NOT NULL "
            "AND length(trim(source_reference)) > 0)",
            name="active_approval_source_required",
        ),
        UniqueConstraint(
            "enterprise_id", "assignment_id", name="uq_assignments_tenant_identity"
        ),
        UniqueConstraint(
            "enterprise_id", "employee_id", "role_id", "department_id",
            "effective_from", name="uq_assignments_effective_identity",
        ),
        Index(
            "ix_assignments_employee_effective",
            "enterprise_id", "employee_id", "effective_from",
        ),
        Index(
            "ix_assignments_role_department_effective",
            "enterprise_id", "role_id", "department_id", "effective_from",
        ),
        Index(
            "uq_assignments_open_primary", "enterprise_id", "role_id",
            "department_id", unique=True,
            sqlite_where=text(
                "is_primary = 1 AND status = 'active' AND effective_to IS NULL"
            ),
            postgresql_where=text(
                "is_primary IS TRUE AND status = 'active' AND effective_to IS NULL"
            ),
        ),
    )

    @validates("effective_from", "effective_to")
    def validate_effective_timestamp(self, key: str, value):
        if value is None and key == "effective_to":
            return None
        if not isinstance(value, datetime) or value.utcoffset() is None:
            raise ValueError(f"Assignment {key} requires a timezone-aware timestamp")
        return value

    @validates("source_reference")
    def normalize_source_reference(self, _key: str, value):
        if value is None:
            return None
        normalized = value.strip()
        if len(normalized) > 255:
            raise ValueError("Assignment source_reference exceeds 255 characters")
        return normalized or None


@event.listens_for(Assignment, "before_update")
def retain_published_assignment(_mapper, _connection, target):
    history = inspect(target).attrs.status.history
    previous_status = history.deleted[0] if history.deleted else target.status
    if previous_status != "pending":
        raise ValueError(
            "Published Assignment rows are immutable; retain history "
            "through an explicit append-only correction"
        )


@event.listens_for(Assignment, "before_delete")
def retain_assignment_history(_mapper, _connection, target):
    history = inspect(target).attrs.status.history
    previous_status = history.deleted[0] if history.deleted else target.status
    if previous_status != "pending" or target.status != "pending":
        raise ValueError("Published Assignment history cannot be deleted")

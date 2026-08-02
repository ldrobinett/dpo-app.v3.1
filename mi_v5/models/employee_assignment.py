"""Historical Employee Assignment aggregate for Management Intelligence v5."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, validates

from mi_v5.database.entities import TenantEntity
from mi_v5.database.mixins import EffectiveDateMixin
from mi_v5.database.types import UUID_TYPE
from mi_v5.enums import EmployeeAssignmentStatus


class EmployeeAssignment(EffectiveDateMixin, TenantEntity):
    """Effective-dated record of one Employee occupying one Position."""

    __tablename__ = "employee_assignments"
    __id_column_name__ = "employee_assignment_id"

    employee_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    position_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    status: Mapped[EmployeeAssignmentStatus] = mapped_column(
        Enum(
            EmployeeAssignmentStatus,
            name="employee_assignment_status",
            native_enum=False,
            validate_strings=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=EmployeeAssignmentStatus.ACTIVE,
        server_default=EmployeeAssignmentStatus.ACTIVE.value,
    )
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="1",
    )
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["enterprise_id", "employee_id"],
            ["employees.enterprise_id", "employees.employee_id"],
            name="fk_employee_assignments_employee",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "position_id"],
            ["positions.enterprise_id", "positions.position_id"],
            name="fk_employee_assignments_position",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="effective_period_valid",
        ),
        UniqueConstraint(
            "enterprise_id",
            "employee_assignment_id",
            name="uq_employee_assignments_tenant_identity",
        ),
        UniqueConstraint(
            "enterprise_id",
            "employee_id",
            "position_id",
            "effective_from",
            name="uq_employee_assignments_employee_position_start",
        ),
        Index(
            "ix_employee_assignments_employee_status",
            "enterprise_id",
            "employee_id",
            "status",
        ),
        Index(
            "ix_employee_assignments_position_status",
            "enterprise_id",
            "position_id",
            "status",
        ),
        Index(
            "uq_employee_assignments_current_primary",
            "enterprise_id",
            "employee_id",
            unique=True,
            sqlite_where=text(
                "is_primary = 1 AND effective_to IS NULL "
                "AND status IN ('pending', 'active', 'leave')"
            ),
            postgresql_where=text(
                "is_primary = true AND effective_to IS NULL "
                "AND status IN ('pending', 'active', 'leave')"
            ),
        ),
    )

    @validates("notes")
    def normalize_notes(self, _key: str, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    def __repr__(self) -> str:
        return (
            "<EmployeeAssignment "
            f"employee_assignment_id={self.id} "
            f"enterprise_id={self.enterprise_id} "
            f"employee_id={self.employee_id} "
            f"position_id={self.position_id} "
            f"status={self.status.value!r} "
            f"is_primary={self.is_primary}>"
        )

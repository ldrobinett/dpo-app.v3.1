"""Canonical Employee aggregate for Management Intelligence v5."""

from __future__ import annotations

import re
from datetime import date

from sqlalchemy import CheckConstraint, Date, Enum, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, validates

from mi_v5.database.entities import TenantEntity
from mi_v5.database.mixins import SoftRetirementMixin
from mi_v5.enums import EmployeeStatus

_EMPLOYEE_NUMBER_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9_-]{0,39}$")
_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Employee(SoftRetirementMixin, TenantEntity):
    """One person employed by an Enterprise, independent of assignment."""

    __tablename__ = "employees"
    __id_column_name__ = "employee_id"

    employee_number: Mapped[str] = mapped_column(String(40), nullable=False)
    external_reference: Mapped[str | None] = mapped_column(String(120), nullable=True)

    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    preferred_name: Mapped[str | None] = mapped_column(String(80), nullable=True)

    work_email: Mapped[str | None] = mapped_column(String(160), nullable=True)
    mobile_phone: Mapped[str | None] = mapped_column(String(40), nullable=True)

    status: Mapped[EmployeeStatus] = mapped_column(
        Enum(
            EmployeeStatus,
            name="employee_status",
            native_enum=False,
            validate_strings=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=EmployeeStatus.ACTIVE,
        server_default=EmployeeStatus.ACTIVE.value,
    )

    hire_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    termination_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    __table_args__ = (
        CheckConstraint("length(trim(first_name)) > 0", name="first_name_required"),
        CheckConstraint("length(trim(last_name)) > 0", name="last_name_required"),
        CheckConstraint(
            "termination_date IS NULL OR hire_date IS NULL OR termination_date >= hire_date",
            name="termination_not_before_hire",
        ),
        UniqueConstraint(
            "enterprise_id",
            "employee_id",
            name="uq_employees_tenant_identity",
        ),
        UniqueConstraint(
            "enterprise_id",
            "employee_number",
            name="uq_employees_enterprise_employee_number",
        ),
        UniqueConstraint(
            "enterprise_id",
            "external_reference",
            name="uq_employees_enterprise_external_reference",
        ),
        UniqueConstraint(
            "enterprise_id",
            "work_email",
            name="uq_employees_enterprise_work_email",
        ),
        Index("ix_employees_enterprise_status", "enterprise_id", "status"),
        Index("ix_employees_enterprise_name", "enterprise_id", "last_name", "first_name"),
    )

    @validates("employee_number")
    def validate_employee_number(self, _key: str, value: str) -> str:
        normalized = value.strip().upper()
        if not _EMPLOYEE_NUMBER_PATTERN.fullmatch(normalized):
            raise ValueError(
                "Employee number must contain 1-40 uppercase letters, digits, underscores, or hyphens."
            )
        return normalized

    @validates("first_name", "last_name")
    def validate_required_name(self, key: str, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError(f"Employee {key.replace('_', ' ')} is required.")
        return normalized

    @validates("middle_name", "preferred_name", "mobile_phone", "external_reference")
    def normalize_optional_text(self, _key: str, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @validates("work_email")
    def validate_work_email(self, _key: str, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if not normalized:
            return None
        if not _EMAIL_PATTERN.fullmatch(normalized):
            raise ValueError("Employee work email is not valid.")
        return normalized

    @property
    def display_name(self) -> str:
        """Preferred display name without embedding assignment or title."""

        given_name = self.preferred_name or self.first_name
        return f"{given_name} {self.last_name}".strip()

    def __repr__(self) -> str:
        return (
            f"<Employee employee_id={self.id} enterprise_id={self.enterprise_id} "
            f"employee_number={self.employee_number!r} display_name={self.display_name!r}>"
        )

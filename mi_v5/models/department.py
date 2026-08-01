"""Canonical Department entity for Management Intelligence v5."""

from __future__ import annotations

import re
from uuid import UUID

from sqlalchemy import CheckConstraint, Enum, ForeignKeyConstraint, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, validates

from mi_v5.database.entities import TenantEntity
from mi_v5.database.mixins import EffectiveDateMixin, SoftRetirementMixin
from mi_v5.database.types import UUID_TYPE
from mi_v5.enums import DepartmentStatus, DepartmentType

_CODE_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9_-]{1,39}$")


class Department(EffectiveDateMixin, SoftRetirementMixin, TenantEntity):
    """Operational accountability unit inside one Managed Store."""

    __tablename__ = "departments"
    __id_column_name__ = "department_id"

    managed_store_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    department_type: Mapped[DepartmentType] = mapped_column(
        Enum(
            DepartmentType,
            name="department_type",
            native_enum=False,
            validate_strings=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    status: Mapped[DepartmentStatus] = mapped_column(
        Enum(
            DepartmentStatus,
            name="department_status",
            native_enum=False,
            validate_strings=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=DepartmentStatus.ACTIVE,
        server_default=DepartmentStatus.ACTIVE.value,
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["enterprise_id", "managed_store_id"],
            ["managed_stores.enterprise_id", "managed_stores.managed_store_id"],
            name="fk_departments_managed_store",
            ondelete="RESTRICT",
        ),
        CheckConstraint("length(trim(name)) > 0", name="name_required"),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="effective_period_valid",
        ),
        UniqueConstraint(
            "enterprise_id",
            "department_id",
            name="uq_departments_tenant_identity",
        ),
        UniqueConstraint(
            "enterprise_id",
            "managed_store_id",
            "code",
            name="uq_departments_store_code",
        ),
        Index(
            "ix_departments_store_status",
            "enterprise_id",
            "managed_store_id",
            "status",
        ),
        Index(
            "ix_departments_store_type",
            "enterprise_id",
            "managed_store_id",
            "department_type",
        ),
    )

    @validates("name")
    def validate_name(self, _key: str, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Department name is required.")
        return normalized

    @validates("code")
    def validate_code(self, _key: str, value: str) -> str:
        normalized = value.strip().upper()
        if not _CODE_PATTERN.fullmatch(normalized):
            raise ValueError(
                "Department code must contain 2-40 uppercase letters, digits, underscores, or hyphens."
            )
        return normalized

    @validates("description")
    def normalize_description(self, _key: str, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    def __repr__(self) -> str:
        return (
            f"<Department department_id={self.id} enterprise_id={self.enterprise_id} "
            f"managed_store_id={self.managed_store_id} code={self.code!r} "
            f"name={self.name!r}>"
        )

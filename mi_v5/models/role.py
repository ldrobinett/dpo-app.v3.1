"""Canonical responsibility and authority Role aggregate for MI v5."""

from __future__ import annotations

import re

from sqlalchemy import CheckConstraint, Enum, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, validates

from mi_v5.database.entities import TenantEntity
from mi_v5.database.mixins import EffectiveDateMixin, SoftRetirementMixin
from mi_v5.enums import RoleStatus

_CODE_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9_-]{1,39}$")


class Role(EffectiveDateMixin, SoftRetirementMixin, TenantEntity):
    """Reusable responsibility and authority definition inside an Enterprise."""

    __tablename__ = "roles"
    __id_column_name__ = "role_id"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[RoleStatus] = mapped_column(
        Enum(
            RoleStatus,
            name="role_status",
            native_enum=False,
            validate_strings=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=RoleStatus.ACTIVE,
        server_default=RoleStatus.ACTIVE.value,
    )

    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="name_required"),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="effective_period_valid",
        ),
        UniqueConstraint(
            "enterprise_id",
            "role_id",
            name="uq_roles_tenant_identity",
        ),
        UniqueConstraint(
            "enterprise_id",
            "code",
            name="uq_roles_enterprise_code",
        ),
        Index("ix_roles_enterprise_status", "enterprise_id", "status"),
        Index("ix_roles_enterprise_name", "enterprise_id", "name"),
    )

    @validates("name")
    def validate_name(self, _key: str, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Role name is required.")
        return normalized

    @validates("code")
    def validate_code(self, _key: str, value: str) -> str:
        normalized = value.strip().upper()
        if not _CODE_PATTERN.fullmatch(normalized):
            raise ValueError(
                "Role code must contain 2-40 uppercase letters, digits, underscores, or hyphens."
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
            f"<Role role_id={self.id} enterprise_id={self.enterprise_id} "
            f"code={self.code!r} name={self.name!r}>"
        )

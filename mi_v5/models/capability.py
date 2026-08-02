"""Canonical business Capability aggregate for Management Intelligence v5."""

from __future__ import annotations

import re

from sqlalchemy import CheckConstraint, Enum, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, validates

from mi_v5.database.entities import TenantEntity
from mi_v5.database.mixins import EffectiveDateMixin, SoftRetirementMixin
from mi_v5.enums import CapabilityStatus

_KEY_PATTERN = re.compile(r"^[a-z0-9]+(?:[._:-][a-z0-9]+)*$")


class Capability(EffectiveDateMixin, SoftRetirementMixin, TenantEntity):
    """One reusable responsibility or authority that may be granted through a Role."""

    __tablename__ = "capabilities"
    __id_column_name__ = "capability_id"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    key: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[CapabilityStatus] = mapped_column(
        Enum(
            CapabilityStatus,
            name="capability_status",
            native_enum=False,
            validate_strings=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=CapabilityStatus.ACTIVE,
        server_default=CapabilityStatus.ACTIVE.value,
    )

    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="name_required"),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="effective_period_valid",
        ),
        UniqueConstraint(
            "enterprise_id",
            "capability_id",
            name="uq_capabilities_tenant_identity",
        ),
        UniqueConstraint(
            "enterprise_id",
            "key",
            name="uq_capabilities_enterprise_key",
        ),
        Index(
            "ix_capabilities_enterprise_status",
            "enterprise_id",
            "status",
        ),
        Index(
            "ix_capabilities_enterprise_category",
            "enterprise_id",
            "category",
        ),
        Index(
            "ix_capabilities_enterprise_name",
            "enterprise_id",
            "name",
        ),
    )

    @validates("name")
    def validate_name(self, _key: str, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Capability name is required.")
        return normalized

    @validates("key")
    def validate_key(self, _key: str, value: str) -> str:
        normalized = value.strip().lower()
        if not _KEY_PATTERN.fullmatch(normalized):
            raise ValueError(
                "Capability key must use lowercase letters, digits, and separators ., _, :, or -."
            )
        return normalized

    @validates("description", "category")
    def normalize_optional_text(
        self, _key: str, value: str | None
    ) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    def __repr__(self) -> str:
        return (
            f"<Capability capability_id={self.id} enterprise_id={self.enterprise_id} "
            f"key={self.key!r} name={self.name!r}>"
        )

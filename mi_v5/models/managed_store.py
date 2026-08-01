"""Canonical Managed Store aggregate for Management Intelligence v5."""

from __future__ import annotations

import re
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKeyConstraint,
    Index,
    JSON,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, validates

from mi_v5.database.entities import TenantEntity
from mi_v5.database.mixins import EffectiveDateMixin, SoftRetirementMixin
from mi_v5.database.types import UUID_TYPE
from mi_v5.enums import ManagedStoreStatus

_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_CODE_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9_-]{1,39}$")
_COUNTRY_PATTERN = re.compile(r"^[A-Z]{2}$")
_REGION_PATTERN = re.compile(r"^[A-Z0-9-]{1,12}$")


class ManagedStore(EffectiveDateMixin, SoftRetirementMixin, TenantEntity):
    """Canonical dealership operating unit inside one Enterprise tenant."""

    __tablename__ = "managed_stores"
    __id_column_name__ = "managed_store_id"

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    store_code: Mapped[str] = mapped_column(String(40), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), nullable=False)
    dealer_code: Mapped[str | None] = mapped_column(String(40), nullable=True)
    external_reference: Mapped[str | None] = mapped_column(String(120), nullable=True)

    status: Mapped[ManagedStoreStatus] = mapped_column(
        Enum(
            ManagedStoreStatus,
            name="managed_store_status",
            native_enum=False,
            validate_strings=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=ManagedStoreStatus.ACTIVE,
        server_default=ManagedStoreStatus.ACTIVE.value,
    )

    timezone: Mapped[str] = mapped_column(String(64), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    state_province_code: Mapped[str | None] = mapped_column(String(12), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)

    primary_brand: Mapped[str | None] = mapped_column(String(80), nullable=True)
    brands: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="name_required"),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="effective_period_valid",
        ),
        UniqueConstraint(
            "enterprise_id",
            "managed_store_id",
            name="uq_managed_stores_tenant_identity",
        ),
        UniqueConstraint(
            "enterprise_id",
            "store_code",
            name="uq_managed_stores_enterprise_store_code",
        ),
        UniqueConstraint(
            "enterprise_id",
            "slug",
            name="uq_managed_stores_enterprise_slug",
        ),
        UniqueConstraint(
            "enterprise_id",
            "dealer_code",
            name="uq_managed_stores_enterprise_dealer_code",
        ),
        UniqueConstraint(
            "enterprise_id",
            "external_reference",
            name="uq_managed_stores_enterprise_external_reference",
        ),
        Index(
            "ix_managed_stores_enterprise_status",
            "enterprise_id",
            "status",
        ),
        Index(
            "ix_managed_stores_enterprise_brand",
            "enterprise_id",
            "primary_brand",
        ),
    )

    @validates("name")
    def validate_name(self, _key: str, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Managed Store name is required.")
        return normalized

    @validates("store_code")
    def validate_store_code(self, _key: str, value: str) -> str:
        normalized = value.strip().upper()
        if not _CODE_PATTERN.fullmatch(normalized):
            raise ValueError(
                "Managed Store code must contain 2-40 uppercase letters, digits, underscores, or hyphens."
            )
        return normalized

    @validates("slug")
    def validate_slug(self, _key: str, value: str) -> str:
        normalized = value.strip().lower()
        if not _SLUG_PATTERN.fullmatch(normalized):
            raise ValueError(
                "Managed Store slug must use lowercase letters, digits, and single hyphens."
            )
        return normalized

    @validates("dealer_code", "external_reference", "primary_brand")
    def normalize_optional_text(self, key: str, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            return None
        if key == "dealer_code":
            return normalized.upper()
        return normalized

    @validates("country_code")
    def validate_country_code(self, _key: str, value: str) -> str:
        normalized = value.strip().upper()
        if not _COUNTRY_PATTERN.fullmatch(normalized):
            raise ValueError("Country code must be ISO 3166-1 alpha-2 format.")
        return normalized

    @validates("state_province_code")
    def validate_state_province_code(
        self, _key: str, value: str | None
    ) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        if not normalized:
            return None
        if not _REGION_PATTERN.fullmatch(normalized):
            raise ValueError("State or province code contains invalid characters.")
        return normalized

    @validates("timezone")
    def validate_timezone(self, _key: str, value: str) -> str:
        normalized = value.strip()
        if normalized != "UTC" and "/" not in normalized:
            raise ValueError(
                "Timezone must be an IANA timezone such as America/Los_Angeles or UTC."
            )
        return normalized

    @validates("brands")
    def validate_brands(
        self, _key: str, value: list[str] | None
    ) -> list[str] | None:
        if value is None:
            return None
        normalized = sorted({brand.strip() for brand in value if brand and brand.strip()})
        return normalized or None

    def __repr__(self) -> str:
        return (
            f"<ManagedStore managed_store_id={self.id} "
            f"enterprise_id={self.enterprise_id} store_code={self.store_code!r} "
            f"name={self.name!r}>"
        )


class ManagedStoreGroupMembership(EffectiveDateMixin, TenantEntity):
    """Effective-dated membership of a Managed Store in an Organizational Group."""

    __tablename__ = "managed_store_group_memberships"
    __id_column_name__ = "managed_store_group_membership_id"

    managed_store_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    organizational_group_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["enterprise_id", "managed_store_id"],
            ["managed_stores.enterprise_id", "managed_stores.managed_store_id"],
            name="fk_managed_store_group_memberships_managed_store",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "organizational_group_id"],
            [
                "organizational_groups.enterprise_id",
                "organizational_groups.organizational_group_id",
            ],
            name="fk_managed_store_group_memberships_organizational_group",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="effective_period_valid",
        ),
        UniqueConstraint(
            "enterprise_id",
            "managed_store_id",
            "organizational_group_id",
            "effective_from",
            name="uq_managed_store_group_memberships_effective_membership",
        ),
        Index(
            "ix_managed_store_group_memberships_store",
            "enterprise_id",
            "managed_store_id",
        ),
        Index(
            "ix_managed_store_group_memberships_group",
            "enterprise_id",
            "organizational_group_id",
        ),
    )

    def __repr__(self) -> str:
        return (
            "<ManagedStoreGroupMembership "
            f"managed_store_id={self.managed_store_id} "
            f"organizational_group_id={self.organizational_group_id}>"
        )

"""Enterprise tenant-root entity for Management Intelligence v5."""

from __future__ import annotations

import re
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, Index, String, func, inspect
from sqlalchemy.orm import Mapped, mapped_column, validates

from mi_v5.database import MIEntity, SoftRetirementMixin
from mi_v5.enums import EnterpriseStatus

_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_CODE_PATTERN = re.compile(r"^[A-Z0-9]{2,10}$")
_COUNTRY_PATTERN = re.compile(r"^[A-Z]{2}$")


class Enterprise(SoftRetirementMixin, MIEntity):
    """One subscribing organization and the root of an MI v5 tenant."""

    __tablename__ = "enterprises"
    __id_column_name__ = "enterprise_id"

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    enterprise_code: Mapped[str] = mapped_column(
        String(10), nullable=False, unique=True
    )
    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    status: Mapped[EnterpriseStatus] = mapped_column(
        Enum(
            EnterpriseStatus,
            name="enterprise_status",
            native_enum=False,
            validate_strings=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=EnterpriseStatus.ACTIVE,
        server_default=EnterpriseStatus.ACTIVE.value,
    )
    external_reference: Mapped[str | None] = mapped_column(
        String(120), nullable=True, unique=True
    )
    default_timezone: Mapped[str] = mapped_column(String(64), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    activated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="name_required"),
        CheckConstraint(
            "retired_at IS NULL OR retired_at >= activated_at",
            name="retirement_after_activation",
        ),
        Index("ix_enterprises_status", "status"),
    )

    @validates("name")
    def validate_name(self, _key: str, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Enterprise name is required.")
        return normalized

    @validates("enterprise_code")
    def validate_enterprise_code(self, key: str, value: str) -> str:
        normalized = value.strip().upper()
        if not _CODE_PATTERN.fullmatch(normalized):
            raise ValueError(
                "Enterprise code must contain 2-10 uppercase letters or digits."
            )
        self._assert_immutable(key, normalized)
        return normalized

    @validates("slug")
    def validate_slug(self, key: str, value: str) -> str:
        normalized = value.strip().lower()
        if not _SLUG_PATTERN.fullmatch(normalized):
            raise ValueError(
                "Enterprise slug must use lowercase letters, digits, and single hyphens."
            )
        self._assert_immutable(key, normalized)
        return normalized

    @validates("country_code")
    def validate_country_code(self, _key: str, value: str) -> str:
        normalized = value.strip().upper()
        if not _COUNTRY_PATTERN.fullmatch(normalized):
            raise ValueError("Country code must be ISO 3166-1 alpha-2 format.")
        return normalized

    @validates("default_timezone")
    def validate_default_timezone(self, _key: str, value: str) -> str:
        normalized = value.strip()
        if "/" not in normalized:
            raise ValueError(
                "Default timezone must be an IANA timezone such as America/Los_Angeles."
            )
        return normalized

    def _assert_immutable(self, attribute_name: str, new_value: str) -> None:
        state = inspect(self)
        current_value = self.__dict__.get(attribute_name)
        if state.persistent and current_value is not None and current_value != new_value:
            raise ValueError(
                f"Enterprise {attribute_name} is immutable after creation."
            )

    def __repr__(self) -> str:
        return (
            f"<Enterprise enterprise_id={self.id} "
            f"enterprise_code={self.enterprise_code!r} slug={self.slug!r}>"
        )

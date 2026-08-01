"""Canonical organizational Position aggregate for Management Intelligence v5."""

from __future__ import annotations

import re
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    ForeignKeyConstraint,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, validates

from mi_v5.database.entities import TenantEntity
from mi_v5.database.mixins import EffectiveDateMixin, SoftRetirementMixin
from mi_v5.database.types import UUID_TYPE
from mi_v5.enums import PositionStatus

_CODE_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9_-]{1,39}$")


class Position(EffectiveDateMixin, SoftRetirementMixin, TenantEntity):
    """One budgeted organizational job that may be filled by an Employee Assignment."""

    __tablename__ = "positions"
    __id_column_name__ = "position_id"

    department_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[PositionStatus] = mapped_column(
        Enum(
            PositionStatus,
            name="position_status",
            native_enum=False,
            validate_strings=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=PositionStatus.ACTIVE,
        server_default=PositionStatus.ACTIVE.value,
    )
    is_managerial: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
    )
    budgeted_fte: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("1.00"),
        server_default="1.00",
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["enterprise_id", "department_id"],
            ["departments.enterprise_id", "departments.department_id"],
            name="fk_positions_department",
            ondelete="RESTRICT",
        ),
        CheckConstraint("length(trim(title)) > 0", name="title_required"),
        CheckConstraint("budgeted_fte > 0", name="budgeted_fte_positive"),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="effective_period_valid",
        ),
        UniqueConstraint(
            "enterprise_id",
            "position_id",
            name="uq_positions_tenant_identity",
        ),
        UniqueConstraint(
            "enterprise_id",
            "department_id",
            "code",
            name="uq_positions_department_code",
        ),
        Index(
            "ix_positions_department_status",
            "enterprise_id",
            "department_id",
            "status",
        ),
        Index(
            "ix_positions_department_title",
            "enterprise_id",
            "department_id",
            "title",
        ),
    )

    @validates("title")
    def validate_title(self, _key: str, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Position title is required.")
        return normalized

    @validates("code")
    def validate_code(self, _key: str, value: str) -> str:
        normalized = value.strip().upper()
        if not _CODE_PATTERN.fullmatch(normalized):
            raise ValueError(
                "Position code must contain 2-40 uppercase letters, digits, underscores, or hyphens."
            )
        return normalized

    @validates("description")
    def normalize_description(
        self, _key: str, value: str | None
    ) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @validates("budgeted_fte")
    def validate_budgeted_fte(
        self, _key: str, value: Decimal | int | float | str
    ) -> Decimal:
        normalized = Decimal(str(value))
        if normalized <= 0:
            raise ValueError("Position budgeted FTE must be greater than zero.")
        return normalized

    def __repr__(self) -> str:
        return (
            f"<Position position_id={self.id} enterprise_id={self.enterprise_id} "
            f"department_id={self.department_id} code={self.code!r} "
            f"title={self.title!r}>"
        )

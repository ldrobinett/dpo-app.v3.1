"""Enterprise tenant-root entity for Management Intelligence v5."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from mi_v5.database import MIEntity, SoftRetirementMixin, StatusMixin


class Enterprise(StatusMixin, SoftRetirementMixin, MIEntity):
    """One subscribing operating organization and the MI v5 tenant boundary."""

    __tablename__ = "enterprise"

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    external_reference: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
        unique=True,
    )
    default_timezone: Mapped[str] = mapped_column(String(64), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    activated_at: Mapped[datetime | None] = mapped_column(nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('provisioning', 'active', 'suspended', 'retired')",
            name="enterprise_status",
        ),
        Index("ix_enterprise_status", "status"),
        Index("ix_enterprise_slug", "slug"),
    )

    def __repr__(self) -> str:
        return f"<Enterprise enterprise_id={self.id} slug={self.slug!r}>"

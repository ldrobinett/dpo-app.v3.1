"""Composable SQLAlchemy model behaviors for Management Intelligence v5."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from .types import UUID_TYPE, new_uuid


class UUIDPrimaryKeyMixin:
    """UUID identity with a canonical table-specific database column name."""

    @declared_attr
    def id(cls) -> Mapped[UUID]:
        table_name = getattr(cls, "__tablename__", cls.__name__.lower())
        return mapped_column(
            f"{table_name}_id",
            UUID_TYPE,
            primary_key=True,
            default=new_uuid,
        )


class TenantMixin:
    """Required Enterprise tenant context for tenant-owned records."""

    @declared_attr
    def enterprise_id(cls) -> Mapped[UUID]:
        return mapped_column(
            UUID_TYPE,
            ForeignKey("enterprise.enterprise_id", ondelete="RESTRICT"),
            nullable=False,
            index=True,
        )


class AuditMixin:
    """Creation and update audit fields using UTC-aware timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    created_by_id: Mapped[UUID | None] = mapped_column(UUID_TYPE, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    updated_by_id: Mapped[UUID | None] = mapped_column(UUID_TYPE, nullable=True)


class EffectiveDateMixin:
    """Effective dating for organizational and accountability history."""

    effective_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    effective_to: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    @property
    def is_current(self) -> bool:
        return self.effective_to is None


class StatusMixin:
    """Readable string-backed lifecycle status.

    Concrete models may narrow allowed values with model validation or a named
    check constraint once their lifecycle is implemented.
    """

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )


class SoftRetirementMixin:
    """Non-destructive retirement marker for operational master records."""

    retired_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    @property
    def is_retired(self) -> bool:
        return self.retired_at is not None


class VersionMixin:
    """Optimistic concurrency version counter."""

    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    @declared_attr.directive
    def __mapper_args__(cls) -> dict[str, Any]:
        return {"version_id_col": cls.version}

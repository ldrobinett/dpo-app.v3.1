"""Effective-dated Role to Capability grant for Management Intelligence v5."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from mi_v5.database.entities import TenantEntity
from mi_v5.database.mixins import EffectiveDateMixin
from mi_v5.database.types import UUID_TYPE


class RoleCapability(EffectiveDateMixin, TenantEntity):
    """One effective-dated Capability granted to one Role within an Enterprise."""

    __tablename__ = "role_capability_assignments"
    __id_column_name__ = "role_capability_id"

    role_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    capability_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["enterprise_id", "role_id"],
            ["roles.enterprise_id", "roles.role_id"],
            name="fk_role_capability_assignments_role",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "capability_id"],
            ["capabilities.enterprise_id", "capabilities.capability_id"],
            name="fk_role_capability_assignments_capability",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="effective_period_valid",
        ),
        UniqueConstraint(
            "enterprise_id",
            "role_capability_id",
            name="uq_role_capability_assignments_tenant_identity",
        ),
        UniqueConstraint(
            "enterprise_id",
            "role_id",
            "capability_id",
            "effective_from",
            name="uq_role_capability_assignments_effective_grant",
        ),
        Index(
            "ix_role_capability_assignments_role",
            "enterprise_id",
            "role_id",
        ),
        Index(
            "ix_role_capability_assignments_capability",
            "enterprise_id",
            "capability_id",
        ),
    )

    def __repr__(self) -> str:
        return (
            "<RoleCapability "
            f"role_capability_id={self.id} enterprise_id={self.enterprise_id} "
            f"role_id={self.role_id} capability_id={self.capability_id}>"
        )

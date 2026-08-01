"""Organizational Group aggregate for Management Intelligence v5."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, validates

from mi_v5.database.entities import TenantEntity
from mi_v5.database.mixins import EffectiveDateMixin, SoftRetirementMixin
from mi_v5.database.types import UUID_TYPE
from mi_v5.enums import OrganizationalGroupStatus, OrganizationalGroupType


class OrganizationalGroup(
    EffectiveDateMixin,
    SoftRetirementMixin,
    TenantEntity,
):
    """Optional organizational grouping inside one Enterprise tenant."""

    __tablename__ = "organizational_groups"
    __id_column_name__ = "organizational_group_id"

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    code: Mapped[str | None] = mapped_column(String(40), nullable=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    group_type: Mapped[OrganizationalGroupType] = mapped_column(
        Enum(
            OrganizationalGroupType,
            name="organizational_group_type",
            native_enum=False,
            validate_strings=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    status: Mapped[OrganizationalGroupStatus] = mapped_column(
        Enum(
            OrganizationalGroupStatus,
            name="organizational_group_status",
            native_enum=False,
            validate_strings=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=OrganizationalGroupStatus.ACTIVE,
        server_default=OrganizationalGroupStatus.ACTIVE.value,
    )

    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="name_required"),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="effective_period_valid",
        ),
        UniqueConstraint(
            "enterprise_id",
            "organizational_group_id",
            name="uq_organizational_groups_tenant_identity",
        ),
        UniqueConstraint(
            "enterprise_id",
            "code",
            name="uq_organizational_groups_enterprise_code",
        ),
        Index(
            "ix_organizational_groups_enterprise_status",
            "enterprise_id",
            "status",
        ),
        Index(
            "ix_organizational_groups_enterprise_type",
            "enterprise_id",
            "group_type",
        ),
    )

    @validates("name")
    def validate_name(self, _key: str, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Organizational Group name is required.")
        return normalized

    @validates("code")
    def validate_code(self, _key: str, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        if not normalized:
            return None
        if len(normalized) > 40:
            raise ValueError("Organizational Group code cannot exceed 40 characters.")
        return normalized

    def __repr__(self) -> str:
        return (
            f"<OrganizationalGroup organizational_group_id={self.id} "
            f"enterprise_id={self.enterprise_id} name={self.name!r} "
            f"group_type={self.group_type.value!r}>"
        )


class OrganizationalGroupHierarchy(EffectiveDateMixin, TenantEntity):
    """Effective-dated parent-child relationship between Organizational Groups."""

    __tablename__ = "organizational_group_hierarchies"
    __id_column_name__ = "organizational_group_hierarchy_id"

    parent_group_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    child_group_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["enterprise_id", "parent_group_id"],
            [
                "organizational_groups.enterprise_id",
                "organizational_groups.organizational_group_id",
            ],
            name="fk_organizational_group_hierarchies_parent_group",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "child_group_id"],
            [
                "organizational_groups.enterprise_id",
                "organizational_groups.organizational_group_id",
            ],
            name="fk_organizational_group_hierarchies_child_group",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "parent_group_id <> child_group_id",
            name="parent_child_different",
        ),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="effective_period_valid",
        ),
        UniqueConstraint(
            "enterprise_id",
            "parent_group_id",
            "child_group_id",
            "effective_from",
            name="uq_organizational_group_hierarchies_effective_relationship",
        ),
        Index(
            "ix_organizational_group_hierarchies_parent",
            "enterprise_id",
            "parent_group_id",
        ),
        Index(
            "ix_organizational_group_hierarchies_child",
            "enterprise_id",
            "child_group_id",
        ),
    )

    def __repr__(self) -> str:
        return (
            "<OrganizationalGroupHierarchy "
            f"parent_group_id={self.parent_group_id} "
            f"child_group_id={self.child_group_id}>"
        )

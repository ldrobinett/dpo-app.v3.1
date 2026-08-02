"""Canonical effective-dated Team Membership aggregate for MI v5."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, validates

from mi_v5.database.entities import TenantEntity
from mi_v5.database.mixins import EffectiveDateMixin
from mi_v5.database.types import UUID_TYPE
from mi_v5.enums import TeamMembershipStatus, TeamMembershipType


class TeamMembership(EffectiveDateMixin, TenantEntity):
    """One Employee's effective-dated participation on an optional Team."""

    __tablename__ = "team_memberships_v5"
    __id_column_name__ = "team_membership_id"

    team_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    employee_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    membership_type: Mapped[TeamMembershipType] = mapped_column(
        Enum(
            TeamMembershipType,
            name="team_membership_type",
            native_enum=False,
            validate_strings=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=TeamMembershipType.MEMBER,
        server_default=TeamMembershipType.MEMBER.value,
    )
    status: Mapped[TeamMembershipStatus] = mapped_column(
        Enum(
            TeamMembershipStatus,
            name="team_membership_status",
            native_enum=False,
            validate_strings=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=TeamMembershipStatus.ACTIVE,
        server_default=TeamMembershipStatus.ACTIVE.value,
    )
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
    )
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["enterprise_id", "team_id"],
            ["teams_v5.enterprise_id", "teams_v5.team_id"],
            name="fk_team_memberships_v5_team",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "employee_id"],
            ["employees.enterprise_id", "employees.employee_id"],
            name="fk_team_memberships_v5_employee",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="effective_period_valid",
        ),
        UniqueConstraint(
            "enterprise_id",
            "team_membership_id",
            name="uq_team_memberships_v5_tenant_identity",
        ),
        UniqueConstraint(
            "enterprise_id",
            "team_id",
            "employee_id",
            "effective_from",
            name="uq_team_memberships_v5_effective_membership",
        ),
        Index(
            "ix_team_memberships_v5_team",
            "enterprise_id",
            "team_id",
            "status",
        ),
        Index(
            "ix_team_memberships_v5_employee",
            "enterprise_id",
            "employee_id",
            "status",
        ),
        Index(
            "uq_team_memberships_v5_current_primary",
            "enterprise_id",
            "employee_id",
            unique=True,
            sqlite_where=text(
                "is_primary = 1 AND effective_to IS NULL "
                "AND status IN ('pending', 'active')"
            ),
            postgresql_where=text(
                "is_primary = true AND effective_to IS NULL "
                "AND status IN ('pending', 'active')"
            ),
        ),
    )

    @validates("notes")
    def normalize_notes(self, _key: str, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    def __repr__(self) -> str:
        return (
            f"<TeamMembership team_membership_id={self.id} "
            f"enterprise_id={self.enterprise_id} team_id={self.team_id} "
            f"employee_id={self.employee_id} "
            f"membership_type={self.membership_type.value!r} "
            f"is_primary={self.is_primary}>"
        )

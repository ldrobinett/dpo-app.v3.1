"""Canonical optional Team aggregate for Management Intelligence v5."""

from __future__ import annotations

import re
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
from mi_v5.enums import TeamStatus, TeamType

_CODE_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9_-]{1,39}$")


class Team(EffectiveDateMixin, SoftRetirementMixin, TenantEntity):
    """An optional execution unit anchored at no more than one organizational level."""

    __tablename__ = "teams_v5"
    __id_column_name__ = "team_id"

    organizational_group_id: Mapped[UUID | None] = mapped_column(
        UUID_TYPE,
        nullable=True,
    )
    managed_store_id: Mapped[UUID | None] = mapped_column(
        UUID_TYPE,
        nullable=True,
    )
    department_id: Mapped[UUID | None] = mapped_column(
        UUID_TYPE,
        nullable=True,
    )
    leader_employee_id: Mapped[UUID | None] = mapped_column(
        UUID_TYPE,
        nullable=True,
    )

    name: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    purpose: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    team_type: Mapped[TeamType] = mapped_column(
        Enum(
            TeamType,
            name="team_type",
            native_enum=False,
            validate_strings=True,
            values_callable=lambda enum_cls: [
                member.value for member in enum_cls
            ],
        ),
        nullable=False,
        default=TeamType.OPERATIONS,
        server_default=TeamType.OPERATIONS.value,
    )
    status: Mapped[TeamStatus] = mapped_column(
        Enum(
            TeamStatus,
            name="team_status",
            native_enum=False,
            validate_strings=True,
            values_callable=lambda enum_cls: [
                member.value for member in enum_cls
            ],
        ),
        nullable=False,
        default=TeamStatus.ACTIVE,
        server_default=TeamStatus.ACTIVE.value,
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["enterprise_id", "organizational_group_id"],
            [
                "organizational_groups.enterprise_id",
                "organizational_groups.organizational_group_id",
            ],
            name="fk_teams_v5_organizational_group",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "managed_store_id"],
            [
                "managed_stores.enterprise_id",
                "managed_stores.managed_store_id",
            ],
            name="fk_teams_v5_managed_store",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "department_id"],
            [
                "departments.enterprise_id",
                "departments.department_id",
            ],
            name="fk_teams_v5_department",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "leader_employee_id"],
            [
                "employees.enterprise_id",
                "employees.employee_id",
            ],
            name="fk_teams_v5_leader_employee",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "length(trim(name)) > 0",
            name="name_required",
        ),
        CheckConstraint(
            """
            (
                CASE
                    WHEN organizational_group_id IS NOT NULL
                    THEN 1
                    ELSE 0
                END
                +
                CASE
                    WHEN managed_store_id IS NOT NULL
                    THEN 1
                    ELSE 0
                END
                +
                CASE
                    WHEN department_id IS NOT NULL
                    THEN 1
                    ELSE 0
                END
            ) <= 1
            """,
            name="single_organizational_anchor",
        ),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="effective_period_valid",
        ),
        UniqueConstraint(
            "enterprise_id",
            "team_id",
            name="uq_teams_v5_tenant_identity",
        ),
        UniqueConstraint(
            "enterprise_id",
            "code",
            name="uq_teams_v5_enterprise_code",
        ),
        Index(
            "ix_teams_v5_enterprise_status",
            "enterprise_id",
            "status",
        ),
        Index(
            "ix_teams_v5_enterprise_type",
            "enterprise_id",
            "team_type",
        ),
        Index(
            "ix_teams_v5_organizational_group",
            "enterprise_id",
            "organizational_group_id",
        ),
        Index(
            "ix_teams_v5_managed_store",
            "enterprise_id",
            "managed_store_id",
        ),
        Index(
            "ix_teams_v5_department",
            "enterprise_id",
            "department_id",
        ),
        Index(
            "ix_teams_v5_leader",
            "enterprise_id",
            "leader_employee_id",
        ),
    )

    @validates("name")
    def validate_name(self, _key: str, value: str) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("Team name is required.")

        return normalized

    @validates("code")
    def validate_code(self, _key: str, value: str) -> str:
        normalized = value.strip().upper()

        if not _CODE_PATTERN.fullmatch(normalized):
            raise ValueError(
                "Team code must contain 2-40 uppercase letters, "
                "digits, underscores, or hyphens."
            )

        return normalized

    @validates("description", "purpose")
    def normalize_optional_text(
        self,
        _key: str,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        return normalized or None

    def __repr__(self) -> str:
        return (
            f"<Team team_id={self.id} "
            f"enterprise_id={self.enterprise_id} "
            f"code={self.code!r} "
            f"name={self.name!r} "
            f"team_type={self.team_type.value!r}>"
        )
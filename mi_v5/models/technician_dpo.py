"""Effective-dated technician Daily Production Objective governance."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    Float,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from mi_v5.database.entities import TenantEntity
from mi_v5.database.types import UUID_TYPE


class TechnicianDPORecord(TenantEntity):
    """One immutable, authorized DPO value for an effective date range.

    ``legacy_team_member_id`` is an explicit vertical-slice bridge. It keeps the
    current application operational until legacy technicians are mapped to the
    canonical Employee aggregate; it is not a replacement employee identity.
    """

    __tablename__ = "technician_dpo_records"
    __id_column_name__ = "technician_dpo_record_id"

    managed_store_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    department_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    legacy_team_member_id: Mapped[int] = mapped_column(Integer, nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    dpo_value: Mapped[float] = mapped_column(Float, nullable=False)
    calculation_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    calculated_dpo: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_override: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0"
    )
    authority_status: Mapped[str] = mapped_column(String(20), nullable=False)
    authorized_by_id: Mapped[UUID | None] = mapped_column(UUID_TYPE, nullable=True)
    authorization_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    calculation_inputs_json: Mapped[str] = mapped_column(Text, nullable=False)
    source_reference: Mapped[str] = mapped_column(String(255), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["enterprise_id", "managed_store_id"],
            ["managed_stores.enterprise_id", "managed_stores.managed_store_id"],
            name="fk_technician_dpo_records_store",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "department_id"],
            ["departments.enterprise_id", "departments.department_id"],
            name="fk_technician_dpo_records_department",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "authorized_by_id"],
            ["employees.enterprise_id", "employees.employee_id"],
            name="fk_technician_dpo_records_authority",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["legacy_team_member_id"],
            ["team_member.id"],
            name="fk_technician_dpo_records_legacy_team_member",
            ondelete="RESTRICT",
        ),
        CheckConstraint("dpo_value >= 0", name="dpo_nonnegative"),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="effective_period_valid",
        ),
        CheckConstraint(
            "authority_status != 'verified' OR "
            "(authorized_by_id IS NOT NULL AND authorization_reason IS NOT NULL "
            "AND length(trim(authorization_reason)) > 0)",
            name="verified_authority_required",
        ),
        CheckConstraint(
            "authority_status IN ('verified', 'provisional', 'unverified_legacy')",
            name="authority_status_valid",
        ),
        CheckConstraint(
            "calculation_mode IN ('manual', 'calculated')",
            name="calculation_mode_valid",
        ),
        UniqueConstraint(
            "enterprise_id",
            "technician_dpo_record_id",
            name="uq_technician_dpo_records_tenant_identity",
        ),
        UniqueConstraint(
            "enterprise_id",
            "legacy_team_member_id",
            "effective_from",
            name="uq_technician_dpo_records_effective_start",
        ),
        Index(
            "ix_technician_dpo_records_effective",
            "enterprise_id",
            "managed_store_id",
            "department_id",
            "legacy_team_member_id",
            "effective_from",
            "effective_to",
        ),
        Index(
            "uq_technician_dpo_records_current",
            "enterprise_id",
            "legacy_team_member_id",
            unique=True,
            sqlite_where=text("effective_to IS NULL"),
            postgresql_where=text("effective_to IS NULL"),
        ),
    )

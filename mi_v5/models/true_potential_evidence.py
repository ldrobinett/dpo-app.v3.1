"""Immutable evidence pack supporting a period True Potential assessment."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKeyConstraint,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from mi_v5.database.entities import TenantEntity
from mi_v5.database.types import UUID_TYPE
from mi_v5.enums import DemandEvidenceStatus, DPOGovernanceStatus


class TruePotentialEvidencePack(TenantEntity):
    """Observed input state retained without upgrading unsupported authority."""

    __tablename__ = "true_potential_evidence_packs"
    __id_column_name__ = "true_potential_evidence_pack_id"

    managed_store_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    department_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    demand_status: Mapped[DemandEvidenceStatus] = mapped_column(
        Enum(
            DemandEvidenceStatus,
            name="demand_evidence_status",
            native_enum=False,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )
    supported_demand_frh: Mapped[float | None] = mapped_column(Float, nullable=True)
    dpo_governance_status: Mapped[DPOGovernanceStatus] = mapped_column(
        Enum(
            DPOGovernanceStatus,
            name="dpo_governance_status",
            native_enum=False,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )
    snapshot_json: Mapped[str] = mapped_column(Text, nullable=False)
    source_trace_json: Mapped[str] = mapped_column(Text, nullable=False)
    limitations_json: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["enterprise_id", "managed_store_id"],
            ["managed_stores.enterprise_id", "managed_stores.managed_store_id"],
            name="fk_true_potential_evidence_packs_store",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "department_id"],
            ["departments.enterprise_id", "departments.department_id"],
            name="fk_true_potential_evidence_packs_department",
            ondelete="RESTRICT",
        ),
        CheckConstraint("period_end >= period_start", name="period_valid"),
        CheckConstraint(
            "(demand_status = 'supported' AND supported_demand_frh IS NOT NULL) "
            "OR (demand_status != 'supported')",
            name="supported_demand_value_required",
        ),
        UniqueConstraint(
            "enterprise_id",
            "true_potential_evidence_pack_id",
            name="uq_true_potential_evidence_packs_tenant_identity",
        ),
        UniqueConstraint(
            "enterprise_id",
            "content_hash",
            name="uq_true_potential_evidence_packs_content_hash",
        ),
        Index(
            "ix_true_potential_evidence_packs_period",
            "enterprise_id",
            "managed_store_id",
            "department_id",
            "period_start",
            "period_end",
            "observed_at",
        ),
    )

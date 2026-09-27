"""Canonical persisted records for Recommendation, Decision, and Action."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKeyConstraint,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from mi_v5.database.entities import TenantEntity
from mi_v5.database.types import UUID_TYPE
from mi_v5.enums import (
    DecisionDisposition,
    ManagementActionStatus,
    RecommendationStatus,
)


class RecommendationOutput(TenantEntity):
    """Advisory proposed response produced from an evidence-backed finding."""

    __tablename__ = "recommendation_outputs"
    __id_column_name__ = "recommendation_output_id"

    managed_store_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    department_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    supersedes_recommendation_output_id: Mapped[UUID | None] = mapped_column(
        UUID_TYPE, nullable=True
    )
    case_id: Mapped[str] = mapped_column(String(180), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    proposed_response: Mapped[str] = mapped_column(Text, nullable=False)
    expected_effect: Mapped[str] = mapped_column(Text, nullable=False)
    attention_class: Mapped[str] = mapped_column(String(16), nullable=False)
    assumptions_json: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_trace_json: Mapped[str] = mapped_column(Text, nullable=False)
    snapshot_json: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[RecommendationStatus] = mapped_column(
        Enum(
            RecommendationStatus,
            name="recommendation_status",
            native_enum=False,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=RecommendationStatus.ACTIVE,
        server_default=RecommendationStatus.ACTIVE.value,
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["enterprise_id", "managed_store_id"],
            ["managed_stores.enterprise_id", "managed_stores.managed_store_id"],
            name="fk_recommendation_outputs_managed_store",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "department_id"],
            ["departments.enterprise_id", "departments.department_id"],
            name="fk_recommendation_outputs_department",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "length(trim(proposed_response)) > 0",
            name="proposed_response_required",
        ),
        UniqueConstraint(
            "enterprise_id",
            "content_hash",
            name="uq_recommendation_outputs_content_hash",
        ),
        UniqueConstraint(
            "enterprise_id",
            "recommendation_output_id",
            name="uq_recommendation_outputs_tenant_identity",
        ),
        Index(
            "uq_recommendation_outputs_supersedes_once",
            "enterprise_id",
            "supersedes_recommendation_output_id",
            unique=True,
        ),
        Index(
            "ix_recommendation_outputs_case",
            "enterprise_id",
            "case_id",
            "generated_at",
        ),
        Index(
            "uq_recommendation_outputs_active_case",
            "enterprise_id",
            "case_id",
            unique=True,
            sqlite_where=text("status = 'active'"),
            postgresql_where=text("status = 'active'"),
        ),
    )


class ManagementDecision(TenantEntity):
    """Immutable accountable human choice concerning a Recommendation Output."""

    __tablename__ = "management_decisions"
    __id_column_name__ = "management_decision_id"

    recommendation_output_id: Mapped[UUID | None] = mapped_column(
        UUID_TYPE, nullable=True
    )
    managed_store_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    department_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    accountable_owner_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    disposition: Mapped[DecisionDisposition] = mapped_column(
        Enum(
            DecisionDisposition,
            name="decision_disposition",
            native_enum=False,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )
    decision_statement: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    original_context_json: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["enterprise_id", "recommendation_output_id"],
            [
                "recommendation_outputs.enterprise_id",
                "recommendation_outputs.recommendation_output_id",
            ],
            name="fk_management_decisions_recommendation",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "managed_store_id"],
            ["managed_stores.enterprise_id", "managed_stores.managed_store_id"],
            name="fk_management_decisions_managed_store",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "department_id"],
            ["departments.enterprise_id", "departments.department_id"],
            name="fk_management_decisions_department",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "accountable_owner_id"],
            ["employees.enterprise_id", "employees.employee_id"],
            name="fk_management_decisions_owner",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "length(trim(decision_statement)) > 0",
            name="decision_statement_required",
        ),
        CheckConstraint(
            "length(trim(rationale)) > 0", name="decision_rationale_required"
        ),
        UniqueConstraint(
            "enterprise_id",
            "management_decision_id",
            name="uq_management_decisions_tenant_identity",
        ),
        UniqueConstraint(
            "enterprise_id",
            "recommendation_output_id",
            name="uq_management_decisions_recommendation",
        ),
        Index(
            "ix_management_decisions_owner_time",
            "enterprise_id",
            "accountable_owner_id",
            "decided_at",
        ),
    )


class ManagementAction(TenantEntity):
    """Specific accountable work created by a Management Decision."""

    __tablename__ = "management_actions"
    __id_column_name__ = "management_action_id"

    management_decision_id: Mapped[UUID] = mapped_column(
        UUID_TYPE, nullable=False
    )
    owner_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    action_text: Mapped[str] = mapped_column(Text, nullable=False)
    completion_condition: Mapped[str] = mapped_column(Text, nullable=False)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[ManagementActionStatus] = mapped_column(
        Enum(
            ManagementActionStatus,
            name="management_action_status",
            native_enum=False,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=ManagementActionStatus.PLANNED,
        server_default=ManagementActionStatus.PLANNED.value,
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["enterprise_id", "management_decision_id"],
            [
                "management_decisions.enterprise_id",
                "management_decisions.management_decision_id",
            ],
            name="fk_management_actions_decision",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "owner_id"],
            ["employees.enterprise_id", "employees.employee_id"],
            name="fk_management_actions_owner",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "length(trim(action_text)) > 0", name="action_text_required"
        ),
        CheckConstraint(
            "length(trim(completion_condition)) > 0",
            name="completion_condition_required",
        ),
        UniqueConstraint(
            "enterprise_id",
            "management_action_id",
            name="uq_management_actions_tenant_identity",
        ),
        Index(
            "ix_management_actions_owner_due",
            "enterprise_id",
            "owner_id",
            "due_at",
        ),
    )

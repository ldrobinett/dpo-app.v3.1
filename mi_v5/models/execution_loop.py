"""Canonical persisted records for execution proof, Validation, and Outcome."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
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
from mi_v5.enums import (
    ExecutionEvidenceType,
    OutcomeClassification,
    ValidationResult,
)


class ExecutionEvidence(TenantEntity):
    """Append-only proof of what Action work occurred, when, and by whom."""

    __tablename__ = "execution_evidence"
    __id_column_name__ = "execution_evidence_id"

    management_action_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    recorded_by_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    evidence_type: Mapped[ExecutionEvidenceType] = mapped_column(
        Enum(
            ExecutionEvidenceType,
            name="execution_evidence_type",
            native_enum=False,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source_reference: Mapped[str] = mapped_column(String(500), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    claims_completion: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    prior_action_status: Mapped[str] = mapped_column(String(24), nullable=False)
    resulting_action_status: Mapped[str] = mapped_column(String(24), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["enterprise_id", "management_action_id"],
            [
                "management_actions.enterprise_id",
                "management_actions.management_action_id",
            ],
            name="fk_execution_evidence_action",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "recorded_by_id"],
            ["employees.enterprise_id", "employees.employee_id"],
            name="fk_execution_evidence_recorder",
            ondelete="RESTRICT",
        ),
        CheckConstraint("length(trim(description)) > 0", name="description_required"),
        CheckConstraint(
            "length(trim(source_reference)) > 0", name="source_reference_required"
        ),
        UniqueConstraint(
            "enterprise_id",
            "execution_evidence_id",
            name="uq_execution_evidence_tenant_identity",
        ),
        Index(
            "ix_execution_evidence_action_time",
            "enterprise_id",
            "management_action_id",
            "occurred_at",
        ),
    )


class Validation(TenantEntity):
    """Append-only expected-versus-observed evaluation using execution proof."""

    __tablename__ = "validations"
    __id_column_name__ = "validation_id"

    management_action_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    validator_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    validated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    evaluation_target: Mapped[str] = mapped_column(Text, nullable=False)
    expected_result: Mapped[str] = mapped_column(Text, nullable=False)
    observed_result: Mapped[str] = mapped_column(Text, nullable=False)
    evaluation_period_start: Mapped[date] = mapped_column(Date, nullable=False)
    evaluation_period_end: Mapped[date] = mapped_column(Date, nullable=False)
    method: Mapped[str] = mapped_column(Text, nullable=False)
    result: Mapped[ValidationResult] = mapped_column(
        Enum(
            ValidationResult,
            name="validation_result",
            native_enum=False,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )
    confidence: Mapped[str] = mapped_column(String(16), nullable=False)
    supporting_evidence_json: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["enterprise_id", "management_action_id"],
            [
                "management_actions.enterprise_id",
                "management_actions.management_action_id",
            ],
            name="fk_validations_action",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "validator_id"],
            ["employees.enterprise_id", "employees.employee_id"],
            name="fk_validations_validator",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "evaluation_period_end >= evaluation_period_start",
            name="evaluation_period_valid",
        ),
        CheckConstraint(
            "length(trim(evaluation_target)) > 0", name="evaluation_target_required"
        ),
        UniqueConstraint(
            "enterprise_id", "validation_id", name="uq_validations_tenant_identity"
        ),
        Index(
            "ix_validations_action_time",
            "enterprise_id",
            "management_action_id",
            "validated_at",
        ),
    )


class Outcome(TenantEntity):
    """Observed result retained as association, not assumed causation."""

    __tablename__ = "outcomes"
    __id_column_name__ = "outcome_id"

    management_decision_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    management_action_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    validation_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    recorded_by_id: Mapped[UUID] = mapped_column(UUID_TYPE, nullable=False)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    observed_result: Mapped[str] = mapped_column(Text, nullable=False)
    expected_actual_variance: Mapped[str] = mapped_column(Text, nullable=False)
    classification: Mapped[OutcomeClassification] = mapped_column(
        Enum(
            OutcomeClassification,
            name="outcome_classification",
            native_enum=False,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )
    supporting_evidence_json: Mapped[str] = mapped_column(Text, nullable=False)
    association_only: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="1"
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["enterprise_id", "management_decision_id"],
            [
                "management_decisions.enterprise_id",
                "management_decisions.management_decision_id",
            ],
            name="fk_outcomes_decision",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "management_action_id"],
            [
                "management_actions.enterprise_id",
                "management_actions.management_action_id",
            ],
            name="fk_outcomes_action",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "validation_id"],
            ["validations.enterprise_id", "validations.validation_id"],
            name="fk_outcomes_validation",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "recorded_by_id"],
            ["employees.enterprise_id", "employees.employee_id"],
            name="fk_outcomes_recorder",
            ondelete="RESTRICT",
        ),
        CheckConstraint("period_end >= period_start", name="period_valid"),
        CheckConstraint("association_only IS TRUE", name="association_only_required"),
        UniqueConstraint(
            "enterprise_id", "outcome_id", name="uq_outcomes_tenant_identity"
        ),
        Index(
            "ix_outcomes_decision_time",
            "enterprise_id",
            "management_decision_id",
            "observed_at",
        ),
    )

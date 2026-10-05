"""Create MI v5 execution evidence, validation, and outcome records

Revision ID: b59e8d2f3a01
Revises: a48d7c1e2f90
Create Date: 2026-09-26 22:00:00

"""

from alembic import op
import sqlalchemy as sa


revision = "b59e8d2f3a01"
down_revision = "a48d7c1e2f90"
branch_labels = None
depends_on = None


def _audit_columns() -> list[sa.Column]:
    return [
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("updated_by_id", sa.Uuid(), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
    ]


def upgrade():
    op.create_table(
        "execution_evidence",
        sa.Column("management_action_id", sa.Uuid(), nullable=False),
        sa.Column("recorded_by_id", sa.Uuid(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "evidence_type",
            sa.Enum(
                "source_reconciliation",
                "system_record",
                "document",
                "observation",
                "approved_exception",
                name="execution_evidence_type",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("source_reference", sa.String(length=500), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column(
            "claims_completion", sa.Boolean(), server_default="0", nullable=False
        ),
        sa.Column("prior_action_status", sa.String(length=24), nullable=False),
        sa.Column("resulting_action_status", sa.String(length=24), nullable=False),
        sa.Column("enterprise_id", sa.Uuid(), nullable=False),
        sa.Column("execution_evidence_id", sa.Uuid(), nullable=False),
        *_audit_columns(),
        sa.CheckConstraint(
            "length(trim(description)) > 0",
            name=op.f("ck_execution_evidence_description_required"),
        ),
        sa.CheckConstraint(
            "length(trim(source_reference)) > 0",
            name=op.f("ck_execution_evidence_source_reference_required"),
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id", "management_action_id"],
            [
                "management_actions.enterprise_id",
                "management_actions.management_action_id",
            ],
            name="fk_execution_evidence_action",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id", "recorded_by_id"],
            ["employees.enterprise_id", "employees.employee_id"],
            name="fk_execution_evidence_recorder",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id"],
            ["enterprises.enterprise_id"],
            name=op.f("fk_execution_evidence_enterprise_id_enterprises"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "execution_evidence_id", name=op.f("pk_execution_evidence")
        ),
        sa.UniqueConstraint(
            "enterprise_id",
            "execution_evidence_id",
            name="uq_execution_evidence_tenant_identity",
        ),
    )
    op.create_index(
        "ix_execution_evidence_action_time",
        "execution_evidence",
        ["enterprise_id", "management_action_id", "occurred_at"],
    )
    op.create_index(
        op.f("ix_execution_evidence_enterprise_id"),
        "execution_evidence",
        ["enterprise_id"],
    )

    op.create_table(
        "validations",
        sa.Column("management_action_id", sa.Uuid(), nullable=False),
        sa.Column("validator_id", sa.Uuid(), nullable=False),
        sa.Column(
            "validated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("evaluation_target", sa.Text(), nullable=False),
        sa.Column("expected_result", sa.Text(), nullable=False),
        sa.Column("observed_result", sa.Text(), nullable=False),
        sa.Column("evaluation_period_start", sa.Date(), nullable=False),
        sa.Column("evaluation_period_end", sa.Date(), nullable=False),
        sa.Column("method", sa.Text(), nullable=False),
        sa.Column(
            "result",
            sa.Enum(
                "achieved",
                "partially_achieved",
                "not_achieved",
                "inconclusive",
                "invalidated",
                name="validation_result",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("confidence", sa.String(length=16), nullable=False),
        sa.Column("supporting_evidence_json", sa.Text(), nullable=False),
        sa.Column("enterprise_id", sa.Uuid(), nullable=False),
        sa.Column("validation_id", sa.Uuid(), nullable=False),
        *_audit_columns(),
        sa.CheckConstraint(
            "evaluation_period_end >= evaluation_period_start",
            name=op.f("ck_validations_evaluation_period_valid"),
        ),
        sa.CheckConstraint(
            "length(trim(evaluation_target)) > 0",
            name=op.f("ck_validations_evaluation_target_required"),
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id", "management_action_id"],
            [
                "management_actions.enterprise_id",
                "management_actions.management_action_id",
            ],
            name="fk_validations_action",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id", "validator_id"],
            ["employees.enterprise_id", "employees.employee_id"],
            name="fk_validations_validator",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id"],
            ["enterprises.enterprise_id"],
            name=op.f("fk_validations_enterprise_id_enterprises"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("validation_id", name=op.f("pk_validations")),
        sa.UniqueConstraint(
            "enterprise_id",
            "validation_id",
            name="uq_validations_tenant_identity",
        ),
    )
    op.create_index(
        "ix_validations_action_time",
        "validations",
        ["enterprise_id", "management_action_id", "validated_at"],
    )
    op.create_index(
        op.f("ix_validations_enterprise_id"),
        "validations",
        ["enterprise_id"],
    )

    op.create_table(
        "outcomes",
        sa.Column("management_decision_id", sa.Uuid(), nullable=False),
        sa.Column("management_action_id", sa.Uuid(), nullable=False),
        sa.Column("validation_id", sa.Uuid(), nullable=False),
        sa.Column("recorded_by_id", sa.Uuid(), nullable=False),
        sa.Column(
            "observed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("observed_result", sa.Text(), nullable=False),
        sa.Column("expected_actual_variance", sa.Text(), nullable=False),
        sa.Column(
            "classification",
            sa.Enum(
                "favorable",
                "neutral",
                "unfavorable",
                "inconclusive",
                name="outcome_classification",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("supporting_evidence_json", sa.Text(), nullable=False),
        sa.Column(
            "association_only", sa.Boolean(), server_default="1", nullable=False
        ),
        sa.Column("enterprise_id", sa.Uuid(), nullable=False),
        sa.Column("outcome_id", sa.Uuid(), nullable=False),
        *_audit_columns(),
        sa.CheckConstraint(
            "period_end >= period_start", name=op.f("ck_outcomes_period_valid")
        ),
        sa.CheckConstraint(
            "association_only IS TRUE",
            name=op.f("ck_outcomes_association_only_required"),
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id", "management_decision_id"],
            [
                "management_decisions.enterprise_id",
                "management_decisions.management_decision_id",
            ],
            name="fk_outcomes_decision",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id", "management_action_id"],
            [
                "management_actions.enterprise_id",
                "management_actions.management_action_id",
            ],
            name="fk_outcomes_action",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id", "validation_id"],
            ["validations.enterprise_id", "validations.validation_id"],
            name="fk_outcomes_validation",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id", "recorded_by_id"],
            ["employees.enterprise_id", "employees.employee_id"],
            name="fk_outcomes_recorder",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id"],
            ["enterprises.enterprise_id"],
            name=op.f("fk_outcomes_enterprise_id_enterprises"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("outcome_id", name=op.f("pk_outcomes")),
        sa.UniqueConstraint(
            "enterprise_id", "outcome_id", name="uq_outcomes_tenant_identity"
        ),
    )
    op.create_index(
        "ix_outcomes_decision_time",
        "outcomes",
        ["enterprise_id", "management_decision_id", "observed_at"],
    )
    op.create_index(
        op.f("ix_outcomes_enterprise_id"),
        "outcomes",
        ["enterprise_id"],
    )


def downgrade():
    op.drop_index(op.f("ix_outcomes_enterprise_id"), table_name="outcomes")
    op.drop_index("ix_outcomes_decision_time", table_name="outcomes")
    op.drop_table("outcomes")
    op.drop_index(op.f("ix_validations_enterprise_id"), table_name="validations")
    op.drop_index("ix_validations_action_time", table_name="validations")
    op.drop_table("validations")
    op.drop_index(
        op.f("ix_execution_evidence_enterprise_id"),
        table_name="execution_evidence",
    )
    op.drop_index("ix_execution_evidence_action_time", table_name="execution_evidence")
    op.drop_table("execution_evidence")

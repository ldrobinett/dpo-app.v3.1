"""Create MI v5 recommendation, decision, and action records

Revision ID: a48d7c1e2f90
Revises: 881160180f24
Create Date: 2026-09-26 20:00:00

"""

from alembic import op
import sqlalchemy as sa


revision = "a48d7c1e2f90"
down_revision = "881160180f24"
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
        "recommendation_outputs",
        sa.Column("managed_store_id", sa.Uuid(), nullable=False),
        sa.Column("department_id", sa.Uuid(), nullable=False),
        sa.Column("case_id", sa.String(length=180), nullable=False),
        sa.Column(
            "generated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("proposed_response", sa.Text(), nullable=False),
        sa.Column("expected_effect", sa.Text(), nullable=False),
        sa.Column("attention_class", sa.String(length=16), nullable=False),
        sa.Column("assumptions_json", sa.Text(), nullable=False),
        sa.Column("evidence_trace_json", sa.Text(), nullable=False),
        sa.Column("snapshot_json", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "active",
                "superseded",
                "withdrawn",
                name="recommendation_status",
                native_enum=False,
            ),
            server_default="active",
            nullable=False,
        ),
        sa.Column("enterprise_id", sa.Uuid(), nullable=False),
        sa.Column("recommendation_output_id", sa.Uuid(), nullable=False),
        *_audit_columns(),
        sa.CheckConstraint(
            "length(trim(proposed_response)) > 0",
            name=op.f("ck_recommendation_outputs_proposed_response_required"),
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id", "managed_store_id"],
            ["managed_stores.enterprise_id", "managed_stores.managed_store_id"],
            name="fk_recommendation_outputs_managed_store",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id", "department_id"],
            ["departments.enterprise_id", "departments.department_id"],
            name="fk_recommendation_outputs_department",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id"],
            ["enterprises.enterprise_id"],
            name=op.f(
                "fk_recommendation_outputs_enterprise_id_enterprises"
            ),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "recommendation_output_id",
            name=op.f("pk_recommendation_outputs"),
        ),
        sa.UniqueConstraint(
            "enterprise_id",
            "content_hash",
            name="uq_recommendation_outputs_content_hash",
        ),
        sa.UniqueConstraint(
            "enterprise_id",
            "recommendation_output_id",
            name="uq_recommendation_outputs_tenant_identity",
        ),
    )
    op.create_index(
        "ix_recommendation_outputs_case",
        "recommendation_outputs",
        ["enterprise_id", "case_id", "generated_at"],
    )
    op.create_index(
        op.f("ix_recommendation_outputs_enterprise_id"),
        "recommendation_outputs",
        ["enterprise_id"],
    )

    op.create_table(
        "management_decisions",
        sa.Column("recommendation_output_id", sa.Uuid(), nullable=True),
        sa.Column("managed_store_id", sa.Uuid(), nullable=False),
        sa.Column("department_id", sa.Uuid(), nullable=False),
        sa.Column("accountable_owner_id", sa.Uuid(), nullable=False),
        sa.Column(
            "decided_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "disposition",
            sa.Enum(
                "accept",
                "modify",
                "reject",
                "defer",
                "independent",
                name="decision_disposition",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("decision_statement", sa.Text(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("original_context_json", sa.Text(), nullable=False),
        sa.Column("enterprise_id", sa.Uuid(), nullable=False),
        sa.Column("management_decision_id", sa.Uuid(), nullable=False),
        *_audit_columns(),
        sa.CheckConstraint(
            "length(trim(decision_statement)) > 0",
            name=op.f("ck_management_decisions_decision_statement_required"),
        ),
        sa.CheckConstraint(
            "length(trim(rationale)) > 0",
            name=op.f("ck_management_decisions_decision_rationale_required"),
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id", "recommendation_output_id"],
            [
                "recommendation_outputs.enterprise_id",
                "recommendation_outputs.recommendation_output_id",
            ],
            name="fk_management_decisions_recommendation",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id", "managed_store_id"],
            ["managed_stores.enterprise_id", "managed_stores.managed_store_id"],
            name="fk_management_decisions_managed_store",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id", "department_id"],
            ["departments.enterprise_id", "departments.department_id"],
            name="fk_management_decisions_department",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id", "accountable_owner_id"],
            ["employees.enterprise_id", "employees.employee_id"],
            name="fk_management_decisions_owner",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id"],
            ["enterprises.enterprise_id"],
            name=op.f("fk_management_decisions_enterprise_id_enterprises"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "management_decision_id",
            name=op.f("pk_management_decisions"),
        ),
        sa.UniqueConstraint(
            "enterprise_id",
            "management_decision_id",
            name="uq_management_decisions_tenant_identity",
        ),
        sa.UniqueConstraint(
            "enterprise_id",
            "recommendation_output_id",
            name="uq_management_decisions_recommendation",
        ),
    )
    op.create_index(
        "ix_management_decisions_owner_time",
        "management_decisions",
        ["enterprise_id", "accountable_owner_id", "decided_at"],
    )
    op.create_index(
        op.f("ix_management_decisions_enterprise_id"),
        "management_decisions",
        ["enterprise_id"],
    )

    op.create_table(
        "management_actions",
        sa.Column("management_decision_id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("action_text", sa.Text(), nullable=False),
        sa.Column("completion_condition", sa.Text(), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "planned",
                "in_progress",
                "completed",
                "cancelled",
                name="management_action_status",
                native_enum=False,
            ),
            server_default="planned",
            nullable=False,
        ),
        sa.Column("enterprise_id", sa.Uuid(), nullable=False),
        sa.Column("management_action_id", sa.Uuid(), nullable=False),
        *_audit_columns(),
        sa.CheckConstraint(
            "length(trim(action_text)) > 0",
            name=op.f("ck_management_actions_action_text_required"),
        ),
        sa.CheckConstraint(
            "length(trim(completion_condition)) > 0",
            name=op.f("ck_management_actions_completion_condition_required"),
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id", "management_decision_id"],
            [
                "management_decisions.enterprise_id",
                "management_decisions.management_decision_id",
            ],
            name="fk_management_actions_decision",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id", "owner_id"],
            ["employees.enterprise_id", "employees.employee_id"],
            name="fk_management_actions_owner",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id"],
            ["enterprises.enterprise_id"],
            name=op.f("fk_management_actions_enterprise_id_enterprises"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "management_action_id", name=op.f("pk_management_actions")
        ),
        sa.UniqueConstraint(
            "enterprise_id",
            "management_action_id",
            name="uq_management_actions_tenant_identity",
        ),
    )
    op.create_index(
        "ix_management_actions_owner_due",
        "management_actions",
        ["enterprise_id", "owner_id", "due_at"],
    )
    op.create_index(
        op.f("ix_management_actions_enterprise_id"),
        "management_actions",
        ["enterprise_id"],
    )


def downgrade():
    op.drop_index(
        op.f("ix_management_actions_enterprise_id"),
        table_name="management_actions",
    )
    op.drop_index(
        "ix_management_actions_owner_due", table_name="management_actions"
    )
    op.drop_table("management_actions")

    op.drop_index(
        op.f("ix_management_decisions_enterprise_id"),
        table_name="management_decisions",
    )
    op.drop_index(
        "ix_management_decisions_owner_time",
        table_name="management_decisions",
    )
    op.drop_table("management_decisions")

    op.drop_index(
        op.f("ix_recommendation_outputs_enterprise_id"),
        table_name="recommendation_outputs",
    )
    op.drop_index(
        "ix_recommendation_outputs_case",
        table_name="recommendation_outputs",
    )
    op.drop_table("recommendation_outputs")

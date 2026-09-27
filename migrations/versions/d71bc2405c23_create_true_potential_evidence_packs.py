"""Create immutable True Potential evidence packs

Revision ID: d71bc2405c23
Revises: c6af91304b12
Create Date: 2026-09-27 00:30:00

"""

from alembic import op
import sqlalchemy as sa


revision = "d71bc2405c23"
down_revision = "c6af91304b12"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "true_potential_evidence_packs",
        sa.Column("managed_store_id", sa.Uuid(), nullable=False),
        sa.Column("department_id", sa.Uuid(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column(
            "observed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "demand_status",
            sa.Enum(
                "supported",
                "partial",
                "unavailable",
                name="demand_evidence_status",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("supported_demand_frh", sa.Float(), nullable=True),
        sa.Column(
            "dpo_governance_status",
            sa.Enum(
                "verified",
                "provisional",
                "unverified_legacy",
                name="dpo_governance_status",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("snapshot_json", sa.Text(), nullable=False),
        sa.Column("source_trace_json", sa.Text(), nullable=False),
        sa.Column("limitations_json", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("enterprise_id", sa.Uuid(), nullable=False),
        sa.Column("true_potential_evidence_pack_id", sa.Uuid(), nullable=False),
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
        sa.CheckConstraint(
            "period_end >= period_start",
            name=op.f("ck_true_potential_evidence_packs_period_valid"),
        ),
        sa.CheckConstraint(
            "(demand_status = 'supported' AND supported_demand_frh IS NOT NULL) "
            "OR (demand_status != 'supported')",
            name=op.f(
                "ck_true_potential_evidence_packs_supported_demand_value_required"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id", "managed_store_id"],
            ["managed_stores.enterprise_id", "managed_stores.managed_store_id"],
            name="fk_true_potential_evidence_packs_store",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id", "department_id"],
            ["departments.enterprise_id", "departments.department_id"],
            name="fk_true_potential_evidence_packs_department",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id"],
            ["enterprises.enterprise_id"],
            name=op.f(
                "fk_true_potential_evidence_packs_enterprise_id_enterprises"
            ),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "true_potential_evidence_pack_id",
            name=op.f("pk_true_potential_evidence_packs"),
        ),
        sa.UniqueConstraint(
            "enterprise_id",
            "true_potential_evidence_pack_id",
            name="uq_true_potential_evidence_packs_tenant_identity",
        ),
        sa.UniqueConstraint(
            "enterprise_id",
            "content_hash",
            name="uq_true_potential_evidence_packs_content_hash",
        ),
    )
    op.create_index(
        "ix_true_potential_evidence_packs_period",
        "true_potential_evidence_packs",
        [
            "enterprise_id",
            "managed_store_id",
            "department_id",
            "period_start",
            "period_end",
            "observed_at",
        ],
    )
    op.create_index(
        op.f("ix_true_potential_evidence_packs_enterprise_id"),
        "true_potential_evidence_packs",
        ["enterprise_id"],
    )


def downgrade():
    op.drop_index(
        op.f("ix_true_potential_evidence_packs_enterprise_id"),
        table_name="true_potential_evidence_packs",
    )
    op.drop_index(
        "ix_true_potential_evidence_packs_period",
        table_name="true_potential_evidence_packs",
    )
    op.drop_table("true_potential_evidence_packs")

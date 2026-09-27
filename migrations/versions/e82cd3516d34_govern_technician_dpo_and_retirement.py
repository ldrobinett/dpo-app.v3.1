"""Govern technician DPO and retain retired technicians

Revision ID: e82cd3516d34
Revises: d71bc2405c23
Create Date: 2026-09-27 01:30:00
"""

from alembic import op
import sqlalchemy as sa


revision = "e82cd3516d34"
down_revision = "d71bc2405c23"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("team_member") as batch_op:
        batch_op.add_column(sa.Column("retired_at", sa.DateTime(), nullable=True))
        batch_op.create_index("ix_team_member_retired_at", ["retired_at"])

    op.create_table(
        "technician_dpo_records",
        sa.Column("managed_store_id", sa.Uuid(), nullable=False),
        sa.Column("department_id", sa.Uuid(), nullable=False),
        sa.Column("legacy_team_member_id", sa.Integer(), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("dpo_value", sa.Float(), nullable=False),
        sa.Column("calculation_mode", sa.String(length=20), nullable=False),
        sa.Column("calculated_dpo", sa.Float(), nullable=True),
        sa.Column("is_override", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("authority_status", sa.String(length=20), nullable=False),
        sa.Column("authorized_by_id", sa.Uuid(), nullable=True),
        sa.Column("authorization_reason", sa.Text(), nullable=True),
        sa.Column("calculation_inputs_json", sa.Text(), nullable=False),
        sa.Column("source_reference", sa.String(length=255), nullable=False),
        sa.Column("enterprise_id", sa.Uuid(), nullable=False),
        sa.Column("technician_dpo_record_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_by_id", sa.Uuid(), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint("dpo_value >= 0", name=op.f("ck_technician_dpo_records_dpo_nonnegative")),
        sa.CheckConstraint("effective_to IS NULL OR effective_to >= effective_from", name=op.f("ck_technician_dpo_records_effective_period_valid")),
        sa.CheckConstraint(
            "authority_status != 'verified' OR (authorized_by_id IS NOT NULL AND authorization_reason IS NOT NULL AND length(trim(authorization_reason)) > 0)",
            name=op.f("ck_technician_dpo_records_verified_authority_required"),
        ),
        sa.CheckConstraint("authority_status IN ('verified', 'provisional', 'unverified_legacy')", name=op.f("ck_technician_dpo_records_authority_status_valid")),
        sa.CheckConstraint("calculation_mode IN ('manual', 'calculated')", name=op.f("ck_technician_dpo_records_calculation_mode_valid")),
        sa.ForeignKeyConstraint(["enterprise_id", "managed_store_id"], ["managed_stores.enterprise_id", "managed_stores.managed_store_id"], name="fk_technician_dpo_records_store", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["enterprise_id", "department_id"], ["departments.enterprise_id", "departments.department_id"], name="fk_technician_dpo_records_department", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["enterprise_id", "authorized_by_id"], ["employees.enterprise_id", "employees.employee_id"], name="fk_technician_dpo_records_authority", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["legacy_team_member_id"], ["team_member.id"], name="fk_technician_dpo_records_legacy_team_member", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["enterprise_id"], ["enterprises.enterprise_id"], name=op.f("fk_technician_dpo_records_enterprise_id_enterprises"), ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("technician_dpo_record_id", name=op.f("pk_technician_dpo_records")),
        sa.UniqueConstraint("enterprise_id", "technician_dpo_record_id", name="uq_technician_dpo_records_tenant_identity"),
        sa.UniqueConstraint("enterprise_id", "legacy_team_member_id", "effective_from", name="uq_technician_dpo_records_effective_start"),
    )
    op.create_index(
        "ix_technician_dpo_records_effective", "technician_dpo_records",
        ["enterprise_id", "managed_store_id", "department_id", "legacy_team_member_id", "effective_from", "effective_to"],
    )
    op.create_index(op.f("ix_technician_dpo_records_enterprise_id"), "technician_dpo_records", ["enterprise_id"])
    op.create_index(
        "uq_technician_dpo_records_current", "technician_dpo_records",
        ["enterprise_id", "legacy_team_member_id"], unique=True,
        sqlite_where=sa.text("effective_to IS NULL"),
        postgresql_where=sa.text("effective_to IS NULL"),
    )


def downgrade():
    op.drop_index("uq_technician_dpo_records_current", table_name="technician_dpo_records")
    op.drop_index(op.f("ix_technician_dpo_records_enterprise_id"), table_name="technician_dpo_records")
    op.drop_index("ix_technician_dpo_records_effective", table_name="technician_dpo_records")
    op.drop_table("technician_dpo_records")
    with op.batch_alter_table("team_member") as batch_op:
        batch_op.drop_index("ix_team_member_retired_at")
        batch_op.drop_column("retired_at")

"""Add empty canonical department-scoped Role Assignments.

Revision ID: f1d8c9a4b672
Revises: e82cd3516d34

No staffing backfill, identity creation, or capability grants.
"""

from alembic import op
import sqlalchemy as sa


revision = "f1d8c9a4b672"
down_revision = "e82cd3516d34"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "assignments",
        sa.Column("assignment_id", sa.Uuid(), nullable=False),
        sa.Column("enterprise_id", sa.Uuid(), nullable=False),
        sa.Column("employee_id", sa.Uuid(), nullable=False),
        sa.Column("role_id", sa.Uuid(), nullable=False),
        sa.Column("department_id", sa.Uuid(), nullable=False),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("source_reference", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_by_id", sa.Uuid(), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.PrimaryKeyConstraint("assignment_id", name="pk_assignments"),
        sa.ForeignKeyConstraint(
            ["enterprise_id"], ["enterprises.enterprise_id"],
            name="fk_assignments_enterprise", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id", "employee_id"],
            ["employees.enterprise_id", "employees.employee_id"],
            name="fk_assignments_employee", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id", "role_id"], ["roles.enterprise_id", "roles.role_id"],
            name="fk_assignments_role", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id", "department_id"],
            ["departments.enterprise_id", "departments.department_id"],
            name="fk_assignments_department", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id", "created_by_id"],
            ["employees.enterprise_id", "employees.employee_id"],
            name="fk_assignments_created_by", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["enterprise_id", "updated_by_id"],
            ["employees.enterprise_id", "employees.employee_id"],
            name="fk_assignments_updated_by", ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "effective_to IS NULL OR effective_to > effective_from",
            name=op.f("ck_assignments_effective_period_valid"),
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'active', 'completed', 'cancelled')",
            name=op.f("ck_assignments_status_valid"),
        ),
        sa.CheckConstraint(
            "status != 'active' OR (created_by_id IS NOT NULL "
            "AND source_reference IS NOT NULL "
            "AND length(trim(source_reference)) > 0)",
            name=op.f("ck_assignments_active_approval_source_required"),
        ),
        sa.UniqueConstraint(
            "enterprise_id", "assignment_id", name="uq_assignments_tenant_identity"
        ),
        sa.UniqueConstraint(
            "enterprise_id", "employee_id", "role_id", "department_id",
            "effective_from", name="uq_assignments_effective_identity",
        ),
    )
    op.create_index("ix_assignments_enterprise_id", "assignments", ["enterprise_id"])
    op.create_index(
        "ix_assignments_employee_effective", "assignments",
        ["enterprise_id", "employee_id", "effective_from"],
    )
    op.create_index(
        "ix_assignments_role_department_effective", "assignments",
        ["enterprise_id", "role_id", "department_id", "effective_from"],
    )
    op.create_index(
        "uq_assignments_open_primary", "assignments",
        ["enterprise_id", "role_id", "department_id"], unique=True,
        sqlite_where=sa.text(
            "is_primary = 1 AND status = 'active' AND effective_to IS NULL"
        ),
        postgresql_where=sa.text(
            "is_primary IS TRUE AND status = 'active' AND effective_to IS NULL"
        ),
    )


def downgrade():
    if op.get_context().as_sql:
        raise RuntimeError("Downgrade requires an online empty-table verification")
    connection = op.get_bind()
    # Alembic owns the transaction; retain writer exclusion through all drops.
    if connection.dialect.name == "postgresql":
        connection.execute(sa.text("LOCK TABLE assignments IN ACCESS EXCLUSIVE MODE"))
    elif connection.dialect.name == "sqlite":
        # A zero-row write reserves the writer without changing history rows,
        # including when an outer SQLite transaction is already in progress.
        connection.execute(sa.text("UPDATE assignments SET version = version WHERE 0"))
    else:
        raise RuntimeError("Assignment downgrade writer exclusion is unsupported for this dialect")
    if connection.execute(
        sa.text("SELECT COUNT(*) FROM assignments")
    ).scalar_one():
        raise RuntimeError("Retain published Assignment history; use a forward correction")
    op.drop_index("uq_assignments_open_primary", table_name="assignments")
    op.drop_index("ix_assignments_role_department_effective", table_name="assignments")
    op.drop_index("ix_assignments_employee_effective", table_name="assignments")
    op.drop_index("ix_assignments_enterprise_id", table_name="assignments")
    op.drop_table("assignments")

"""Add governed Recommendation Output resolution and supersession

Revision ID: c6af91304b12
Revises: b59e8d2f3a01
Create Date: 2026-09-26 23:30:00

"""

from alembic import op
import sqlalchemy as sa


revision = "c6af91304b12"
down_revision = "b59e8d2f3a01"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "recommendation_outputs",
        sa.Column(
            "supersedes_recommendation_output_id",
            sa.Uuid(),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE recommendation_outputs
        SET status = 'resolved',
            updated_at = CURRENT_TIMESTAMP,
            version = version + 1
        WHERE EXISTS (
            SELECT 1
            FROM management_decisions md
            WHERE md.enterprise_id = recommendation_outputs.enterprise_id
              AND md.recommendation_output_id =
                  recommendation_outputs.recommendation_output_id
        )
        """
    )
    op.execute(
        """
        WITH ranked AS (
            SELECT recommendation_output_id,
                   ROW_NUMBER() OVER (
                       PARTITION BY enterprise_id, case_id
                       ORDER BY generated_at DESC, created_at DESC
                   ) AS sequence
            FROM recommendation_outputs
            WHERE status = 'active'
        )
        UPDATE recommendation_outputs
        SET status = 'superseded',
            updated_at = CURRENT_TIMESTAMP,
            version = version + 1
        WHERE recommendation_output_id IN (
            SELECT recommendation_output_id FROM ranked WHERE sequence > 1
        )
        """
    )
    op.create_index(
        "uq_recommendation_outputs_supersedes_once",
        "recommendation_outputs",
        ["enterprise_id", "supersedes_recommendation_output_id"],
        unique=True,
    )
    op.create_index(
        "uq_recommendation_outputs_active_case",
        "recommendation_outputs",
        ["enterprise_id", "case_id"],
        unique=True,
        sqlite_where=sa.text("status = 'active'"),
        postgresql_where=sa.text("status = 'active'"),
    )


def downgrade():
    op.drop_index(
        "uq_recommendation_outputs_active_case",
        table_name="recommendation_outputs",
    )
    op.execute(
        """
        UPDATE recommendation_outputs
        SET status = 'active'
        WHERE status IN ('resolved', 'superseded', 'expired')
        """
    )
    op.drop_index(
        "uq_recommendation_outputs_supersedes_once",
        table_name="recommendation_outputs",
    )
    op.drop_column(
        "recommendation_outputs", "supersedes_recommendation_output_id"
    )

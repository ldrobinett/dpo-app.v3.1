"""Store-scoped forecast inputs, preserving every legacy user input row.

Requires operator review of duplicate forecast periods before upgrade.
"""
from alembic import op
import sqlalchemy as sa
revision = 'a93ef4027b18'
down_revision = '3c0ba172b4a0'
branch_labels = None
depends_on = None


def upgrade():
    duplicate = op.get_bind().execute(sa.text('''
        SELECT store_id, year, month FROM financial_forecast
        GROUP BY store_id, year, month HAVING COUNT(*) > 1
    ''')).first()
    if duplicate:
        raise RuntimeError('Duplicate forecast periods exist. Back up and reconcile them explicitly before upgrading; no data was deleted.')
    op.create_table(
        'store_forecast_inputs',
        sa.Column('store_id', sa.Integer(), sa.ForeignKey('managed_store.id'), primary_key=True),
        sa.Column('values', sa.JSON(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
    )
    with op.batch_alter_table('financial_forecast') as batch:
        batch.create_unique_constraint('uq_forecast_store_period', ['store_id', 'year', 'month'])


def downgrade():
    if op.get_bind().execute(sa.text('SELECT 1 FROM store_forecast_inputs LIMIT 1')).first():
        raise RuntimeError('Shared inputs exist. Export and explicitly reconcile them before downgrade.')
    with op.batch_alter_table('financial_forecast') as batch:
        batch.drop_constraint('uq_forecast_store_period', type_='unique')
    op.drop_table('store_forecast_inputs')

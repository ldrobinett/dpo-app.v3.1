"""Migration checks against an isolated in-memory database."""
import importlib.util
from pathlib import Path
from unittest.mock import patch
import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

spec = importlib.util.spec_from_file_location('forecast_migration', Path(__file__).resolve().parents[1] / 'migrations/versions/a93ef4027b18_share_forecast_inputs.py')
migration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration)

@pytest.fixture
def conn():
    engine = sa.create_engine('sqlite://')
    with engine.begin() as conn:
        conn.exec_driver_sql('CREATE TABLE managed_store (id INTEGER PRIMARY KEY)')
        conn.exec_driver_sql('CREATE TABLE user (id INTEGER PRIMARY KEY)')
        conn.exec_driver_sql('CREATE TABLE financial_forecast (id INTEGER PRIMARY KEY, store_id INTEGER, year INTEGER, month INTEGER, total_gross FLOAT)')
        conn.exec_driver_sql('CREATE TABLE financial_inputs (id INTEGER PRIMARY KEY, user_id INTEGER, effective_labor_rate FLOAT)')
        conn.exec_driver_sql('INSERT INTO financial_inputs VALUES (1, 1, 123)')
        with patch.object(migration, 'op', Operations(MigrationContext.configure(conn))):
            yield conn
    engine.dispose()


def test_upgrade_preserves_inputs_and_forecasts_and_enforces_uniqueness(conn):
    conn.exec_driver_sql('INSERT INTO financial_forecast VALUES (1, 1, 2026, 11, 900)')
    migration.upgrade()
    assert conn.exec_driver_sql('SELECT effective_labor_rate FROM financial_inputs').scalar() == 123
    assert conn.exec_driver_sql('SELECT total_gross FROM financial_forecast').scalar() == 900
    with pytest.raises(sa.exc.IntegrityError):
        conn.exec_driver_sql('INSERT INTO financial_forecast VALUES (2, 1, 2026, 11, 800)')


def test_duplicates_block_upgrade_without_silent_reconciliation(conn):
    conn.exec_driver_sql('INSERT INTO financial_forecast VALUES (1, 1, 2026, 11, 900), (2, 1, 2026, 11, 800)')
    with pytest.raises(RuntimeError, match='Duplicate forecast'):
        migration.upgrade()
    assert conn.exec_driver_sql('SELECT COUNT(*) FROM financial_forecast').scalar() == 2
    assert 'store_forecast_inputs' not in sa.inspect(conn).get_table_names()


def test_downgrade_refuses_to_discard_shared_inputs(conn):
    migration.upgrade()
    conn.exec_driver_sql('INSERT INTO store_forecast_inputs (store_id, "values", version, updated_by, updated_at) VALUES (1, \'{}\', 1, 1, CURRENT_TIMESTAMP)')
    with pytest.raises(RuntimeError, match='Shared inputs exist'):
        migration.downgrade()
    assert conn.exec_driver_sql('SELECT COUNT(*) FROM store_forecast_inputs').scalar() == 1


def test_empty_downgrade_retains_legacy_inputs(conn):
    migration.upgrade()
    migration.downgrade()
    assert conn.exec_driver_sql('SELECT effective_labor_rate FROM financial_inputs').scalar() == 123


def test_beta_migration_history_has_one_connected_head():
    from alembic.script import ScriptDirectory
    scripts = ScriptDirectory(str(Path(__file__).resolve().parents[1] / 'migrations'))
    assert scripts.get_heads() == [migration.revision]
    assert migration.down_revision == '3c0ba172b4a0'
    assert scripts.get_revision(migration.down_revision) is not None
    assert list(scripts.walk_revisions())[0].revision == migration.revision

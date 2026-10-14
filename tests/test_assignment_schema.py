from __future__ import annotations

import importlib.util
import io
import sys
import types
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import UUID

DEPENDENCIES = all(importlib.util.find_spec(name) is not None
                   for name in ("sqlalchemy", "alembic"))


@unittest.skipUnless(DEPENDENCIES, "SQLAlchemy/Alembic needed for offline schema tests")
class AssignmentSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load actual model mappings without Flask app startup, secrets or any engine.
        from sqlalchemy import MetaData
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.dialects import postgresql
        from mi_v5.database.naming import NAMING_CONVENTION

        class IsolatedBase(DeclarativeBase):
            metadata = MetaData(naming_convention=NAMING_CONVENTION)

        extensions = types.ModuleType("extensions")
        extensions.db = types.SimpleNamespace(Model=IsolatedBase)
        with patch.dict(sys.modules, {"extensions": extensions}):
            from mi_v5.models import Assignment, EmployeeAssignment
            from mi_v5.models.assignment import (
                retain_assignment_history, retain_published_assignment,
            )
        cls.Assignment = Assignment
        cls.EmployeeAssignment = EmployeeAssignment
        cls.update_guard = staticmethod(retain_published_assignment)
        cls.delete_guard = staticmethod(retain_assignment_history)

    def test_postgresql_ddl_has_tenant_qualified_constraints_and_strict_period(self):
        from sqlalchemy.schema import CreateTable, CreateIndex
        from sqlalchemy.dialects import postgresql
        table = self.Assignment.__table__
        ddl = str(CreateTable(table).compile(dialect=postgresql.dialect()))
        self.assertIn("effective_to > effective_from", ddl)
        for parent, key in (
            ("employees", "employee_id"), ("roles", "role_id"),
            ("departments", "department_id"), ("employees", "created_by_id"),
            ("employees", "updated_by_id"),
        ):
            self.assertIn(f"FOREIGN KEY(enterprise_id, {key})", ddl)
            self.assertIn(f"REFERENCES {parent} (enterprise_id,", ddl)
        self.assertIsNone(table.c.effective_from.server_default)
        self.assertIsNone(table.c.status.server_default)
        self.assertIsNone(table.c.is_primary.server_default)
        self.assertTrue(table.c.effective_to.nullable)
        primary = next(index for index in table.indexes
                       if index.name == "uq_assignments_open_primary")
        index_ddl = str(CreateIndex(primary).compile(dialect=postgresql.dialect()))
        self.assertIn("(enterprise_id, role_id, department_id)", index_ddl)
        self.assertIn("is_primary IS TRUE", index_ddl)
        self.assertNotIn("employee_id", index_ddl)

    def test_staffing_position_relationship_is_unchanged(self):
        table = self.EmployeeAssignment.__table__
        self.assertFalse(table.c.position_id.nullable)
        self.assertNotIn("role_id", table.c)
        self.assertNotIn("position_id", self.Assignment.__table__.c)

    def test_model_rejects_naive_timestamps_and_mutating_published_history(self):
        from sqlalchemy.orm.attributes import set_committed_value
        row = self.Assignment(
            enterprise_id=UUID(int=1), employee_id=UUID(int=2),
            role_id=UUID(int=3), department_id=UUID(int=4),
            effective_from=datetime(2026, 10, 13, tzinfo=timezone.utc),
            status="pending", is_primary=True,
        )
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            row.effective_from = datetime(2026, 10, 13)
        self.update_guard(None, None, row)
        set_committed_value(row, "status", "active")
        row.status = "pending"
        with self.assertRaisesRegex(ValueError, "immutable"):
            self.update_guard(None, None, row)
        row.status = "active"
        with self.assertRaisesRegex(ValueError, "cannot be deleted"):
            self.delete_guard(None, None, row)

    def migration(self):
        path = Path(__file__).resolve().parents[1] / "migrations" / "versions" / \
            "f1d8c9a4b672_add_canonical_assignments.py"
        spec = importlib.util.spec_from_file_location("assignment_migration_test", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_published_assignment_cannot_be_deleted_after_status_changes_to_pending(self):
        from sqlalchemy.orm.attributes import set_committed_value
        for published_status in ("active", "completed", "cancelled"):
            with self.subTest(status=published_status):
                row = self.Assignment(status="pending")
                set_committed_value(row, "status", published_status)
                row.status = "pending"
                with self.assertRaisesRegex(ValueError, "cannot be deleted"):
                    self.delete_guard(None, None, row)
        self.delete_guard(None, None, self.Assignment(status="pending"))

    def offline_upgrade_sql(self):
        from alembic.migration import MigrationContext
        from alembic.operations import Operations
        buffer = io.StringIO()
        context = MigrationContext.configure(dialect_name="postgresql", opts={
            "as_sql": True, "output_buffer": buffer,
            "target_metadata": self.Assignment.metadata,
        })
        migration = self.migration()
        self.assertEqual(migration.down_revision, "e82cd3516d34")
        with Operations.context(context):
            migration.upgrade()  # SQL emission only; no engine or DBAPI connection.
        return buffer.getvalue()

    def test_offline_upgrade_sql_creates_empty_table_only_without_connecting(self):
        sql = self.offline_upgrade_sql()
        self.assertIn("CREATE TABLE assignments", sql)
        self.assertIn("effective_to > effective_from", sql)
        self.assertNotRegex(
            sql.upper(), r"(?m)^\s*(INSERT\s+INTO|UPDATE\s+\w|DELETE\s+FROM|GRANT\s+)"
        )
        self.assertNotIn("ALTER TABLE employee_assignments", sql)

    def test_offline_upgrade_check_names_match_production_metadata(self):
        from sqlalchemy import CheckConstraint
        sql = self.offline_upgrade_sql()
        checks = [constraint for constraint in self.Assignment.__table__.constraints
                  if isinstance(constraint, CheckConstraint)]
        self.assertEqual(len(checks), 3)
        for constraint in checks:
            self.assertIn(f"CONSTRAINT {constraint.name} CHECK", sql)
        self.assertNotIn("ck_assignments_ck_assignments_", sql)

    def test_downgrade_refuses_to_drop_nonempty_history_or_fake_offline_verification(self):
        migration = self.migration()
        operation = MagicMock()
        operation.get_context.return_value.as_sql = False
        operation.get_bind.return_value.dialect.name = "postgresql"
        operation.get_bind.return_value.execute.return_value.scalar_one.return_value = 1
        with patch.object(migration, "op", operation):
            with self.assertRaisesRegex(RuntimeError, "Retain published"):
                migration.downgrade()
        operation.drop_table.assert_not_called()
        operation.get_context.return_value.as_sql = True
        with patch.object(migration, "op", operation):
            with self.assertRaisesRegex(RuntimeError, "online empty-table"):
                migration.downgrade()

    def test_downgrade_excludes_writers_before_count_and_keeps_lock_through_drop(self):
        # Simulated ordering only: this does not validate database concurrency.
        for dialect, lock_sql in (
            ("postgresql", "LOCK TABLE assignments IN ACCESS EXCLUSIVE MODE"),
            ("sqlite", "UPDATE assignments SET version = version WHERE 0"),
        ):
            with self.subTest(dialect=dialect):
                migration = self.migration()
                operation = MagicMock()
                operation.get_context.return_value.as_sql = False
                connection = operation.get_bind.return_value
                connection.dialect.name = dialect
                events = []

                def execute(statement):
                    sql = str(statement)
                    events.append(sql)
                    if sql == lock_sql:
                        return MagicMock()
                    self.assertEqual(sql, "SELECT COUNT(*) FROM assignments")
                    self.assertEqual(events[0], lock_sql)
                    return MagicMock(scalar_one=MagicMock(return_value=0))

                def destructive_operation(*args, **kwargs):
                    self.assertEqual(events[:2], [lock_sql, "SELECT COUNT(*) FROM assignments"])
                    connection.commit.assert_not_called()
                    connection.rollback.assert_not_called()

                connection.execute.side_effect = execute
                operation.drop_index.side_effect = destructive_operation
                operation.drop_table.side_effect = destructive_operation
                with patch.object(migration, "op", operation):
                    migration.downgrade()
                self.assertEqual(operation.drop_index.call_count, 4)
                operation.drop_table.assert_called_once_with("assignments")

    def test_downgrade_stops_before_count_or_drop_if_writer_lock_fails(self):
        for dialect, lock_sql in (
            ("postgresql", "LOCK TABLE assignments IN ACCESS EXCLUSIVE MODE"),
            ("sqlite", "UPDATE assignments SET version = version WHERE 0"),
        ):
            with self.subTest(dialect=dialect):
                migration = self.migration()
                operation = MagicMock()
                operation.get_context.return_value.as_sql = False
                connection = operation.get_bind.return_value
                connection.dialect.name = dialect
                connection.execute.side_effect = RuntimeError("writer lock unavailable")
                with patch.object(migration, "op", operation):
                    with self.assertRaisesRegex(RuntimeError, "writer lock unavailable"):
                        migration.downgrade()
                self.assertEqual(str(connection.execute.call_args.args[0]), lock_sql)
                self.assertEqual(connection.execute.call_count, 1)
                operation.drop_index.assert_not_called()
                operation.drop_table.assert_not_called()

    def test_downgrade_refuses_unknown_writer_exclusion_dialects(self):
        migration = self.migration()
        operation = MagicMock()
        operation.get_context.return_value.as_sql = False
        connection = operation.get_bind.return_value
        connection.dialect.name = "unsupported"
        with patch.object(migration, "op", operation):
            with self.assertRaisesRegex(RuntimeError, "writer exclusion is unsupported"):
                migration.downgrade()
        connection.execute.assert_not_called()
        operation.drop_index.assert_not_called()
        operation.drop_table.assert_not_called()


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import date
from pathlib import Path

from mi_v5.vertical_slice.dpo_governance import (
    apply_current_dpo_plan,
    build_current_dpo_plan,
)


class DPOGovernanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = Path(self.temp_dir.name) / "site.db"
        with closing(sqlite3.connect(self.database)) as connection:
            connection.executescript(
                """
                PRAGMA foreign_keys = ON;
                CREATE TABLE enterprises (enterprise_id TEXT PRIMARY KEY);
                CREATE TABLE managed_stores (
                    managed_store_id TEXT PRIMARY KEY, enterprise_id TEXT
                );
                CREATE TABLE departments (
                    department_id TEXT PRIMARY KEY, enterprise_id TEXT,
                    managed_store_id TEXT, department_type TEXT,
                    effective_from TEXT
                );
                CREATE TABLE employees (
                    employee_id TEXT PRIMARY KEY, enterprise_id TEXT,
                    UNIQUE (enterprise_id, employee_id)
                );
                CREATE TABLE team (id INTEGER PRIMARY KEY, store_id INTEGER);
                CREATE TABLE team_member (
                    id INTEGER PRIMARY KEY, name TEXT, team_id INTEGER,
                    tech_number TEXT,
                    daily_production_objective REAL, dpo_calculation_mode TEXT,
                    hist_frh_total REAL, hist_days_in_period INTEGER,
                    hist_training_days INTEGER, hist_vacation_days INTEGER,
                    expected_lift_percent REAL, retired_at TEXT
                );
                CREATE TABLE technician_dpo_records (
                    technician_dpo_record_id TEXT PRIMARY KEY,
                    enterprise_id TEXT, managed_store_id TEXT,
                    department_id TEXT, legacy_team_member_id INTEGER,
                    effective_from TEXT, effective_to TEXT, dpo_value REAL,
                    calculation_mode TEXT, calculated_dpo REAL,
                    is_override INTEGER, authority_status TEXT,
                    authorized_by_id TEXT, authorization_reason TEXT,
                    calculation_inputs_json TEXT, source_reference TEXT,
                    created_at TEXT, created_by_id TEXT, updated_at TEXT,
                    updated_by_id TEXT, version INTEGER,
                    UNIQUE (enterprise_id, legacy_team_member_id, effective_from)
                );
                INSERT INTO enterprises VALUES ('enterprise-1');
                INSERT INTO managed_stores VALUES ('store-1', 'enterprise-1');
                INSERT INTO departments VALUES (
                    'department-1', 'enterprise-1', 'store-1', 'service',
                    '2026-01-01'
                );
                INSERT INTO employees VALUES ('manager-1', 'enterprise-1');
                INSERT INTO team VALUES (1, 1);
                INSERT INTO team_member VALUES (
                    10, 'Active Tech', 1, '100', 8.0, 'manual', 80.0, 10, 0, 0,
                    100.0, NULL
                );
                INSERT INTO team_member VALUES (
                    11, 'Retired Tech', 1, '101', 9.0, 'manual', 90.0, 10, 0,
                    0, 100.0, '2026-09-01'
                );
                """
            )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _plan(self, effective_from: date):
        return build_current_dpo_plan(
            self.database,
            effective_from,
            "manager-1",
            "Approved prospective operating baseline.",
        )

    def test_authorization_is_active_only_and_idempotent(self) -> None:
        plan = self._plan(date(2026, 10, 1))
        self.assertEqual(len(plan["technicians"]), 1)
        self.assertEqual(apply_current_dpo_plan(self.database, plan)["inserted"], 1)
        second = apply_current_dpo_plan(self.database, plan)
        self.assertEqual(second, {"inserted": 0, "closed": 0, "unchanged": 1})

    def test_new_effective_set_closes_prior_history(self) -> None:
        apply_current_dpo_plan(self.database, self._plan(date(2026, 10, 1)))
        with closing(sqlite3.connect(self.database)) as connection:
            connection.execute(
                "UPDATE team_member SET daily_production_objective = 8.5 WHERE id = 10"
            )
            connection.commit()
        result = apply_current_dpo_plan(
            self.database, self._plan(date(2026, 11, 1))
        )
        self.assertEqual(result, {"inserted": 1, "closed": 1, "unchanged": 0})
        with closing(sqlite3.connect(self.database)) as connection:
            rows = connection.execute(
                "SELECT effective_from, effective_to, dpo_value "
                "FROM technician_dpo_records ORDER BY effective_from"
            ).fetchall()
        self.assertEqual(rows[0], ("2026-10-01", "2026-10-31", 8.0))
        self.assertEqual(rows[1], ("2026-11-01", None, 8.5))

    def test_incomplete_identity_and_dpo_block_apply(self) -> None:
        with closing(sqlite3.connect(self.database)) as connection:
            connection.execute(
                "UPDATE team_member SET tech_number = '', daily_production_objective = 0 "
                "WHERE id = 10"
            )
            connection.commit()
        plan = self._plan(date(2026, 10, 1))
        self.assertTrue(plan["blocking_issues"])
        with self.assertRaisesRegex(ValueError, "DPO plan is blocked"):
            apply_current_dpo_plan(self.database, plan)


if __name__ == "__main__":
    unittest.main()

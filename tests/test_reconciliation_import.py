from __future__ import annotations

import csv
import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import date
from pathlib import Path

from scripts.import_v5_reconciliation import apply_plan, build_plan


SCHEMA = """
CREATE TABLE managed_store (
    id INTEGER PRIMARY KEY,
    tech_hours_audit_timestamp TEXT
);
CREATE TABLE team (
    id INTEGER PRIMARY KEY,
    store_id INTEGER NOT NULL
);
CREATE TABLE team_member (
    id INTEGER PRIMARY KEY,
    team_id INTEGER NOT NULL,
    tech_number TEXT
);
CREATE TABLE work_log (
    id INTEGER PRIMARY KEY,
    team_member_id INTEGER NOT NULL,
    date TEXT,
    actual_time REAL,
    ro_number TEXT,
    line_item TEXT,
    flat_rate_hours REAL NOT NULL,
    notes TEXT
);
"""


class ReconciliationImportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.database = root / "site.db"
        self.backup = root / "site.before-import.db"
        self.source = root / "source.csv"
        with closing(sqlite3.connect(self.database)) as connection:
            with connection:
                connection.executescript(SCHEMA)
                connection.execute("INSERT INTO managed_store (id) VALUES (1)")
                connection.execute("INSERT INTO team VALUES (1, 1)")
                connection.execute("INSERT INTO team_member VALUES (10, 1, '100')")
        header = [f"column-{index}" for index in range(19)]
        known = ["RO-1", "27APR26", "", "", "100", "A"]
        known += [""] * 6 + ["1.0", "2.5"] + [""] * 5
        excluded = ["RO-2", "27APR26", "", "", "6722", "A"]
        excluded += [""] * 6 + ["1.0", "3.0"] + [""] * 5
        with self.source.open("w", encoding="latin-1", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            writer.writerow(known)
            writer.writerow(known)
            writer.writerow(excluded)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _plan(self):
        return build_plan(
            self.database,
            self.source,
            1,
            date(2026, 4, 27),
            date(2026, 4, 30),
            {"6722"},
            "Departed technician excluded from surviving-cohort exercise.",
        )

    def test_apply_is_backed_up_and_multiset_idempotent(self) -> None:
        plan, candidates = self._plan()
        self.assertFalse(plan["blocked"])
        self.assertEqual(plan["proposed_insert_rows"], 2)
        self.assertEqual(plan["proposed_insert_sold_hours"], 5.0)
        self.assertEqual(
            plan["excluded_technicians"]["6722"],
            {"rows": 1, "sold_hours": 3.0},
        )

        apply_plan(self.database, self.backup, plan, candidates)
        self.assertTrue(self.backup.exists())
        second_plan, second_candidates = self._plan()
        self.assertEqual(second_plan["already_present_rows"], 2)
        self.assertEqual(second_plan["proposed_insert_rows"], 0)
        self.assertEqual(second_candidates, [])

    def test_unmapped_technician_blocks_apply_plan(self) -> None:
        plan, _ = build_plan(
            self.database,
            self.source,
            1,
            date(2026, 4, 27),
            date(2026, 4, 30),
            set(),
            "",
        )
        self.assertTrue(plan["blocked"])
        self.assertIn("6722", plan["unmapped_technicians"])


if __name__ == "__main__":
    unittest.main()

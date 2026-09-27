from __future__ import annotations

import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import date
from pathlib import Path

from mi_v5.vertical_slice.evidence_pack import (
    build_evidence_pack,
    persist_evidence_pack,
)


class EvidencePackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = Path(self.temp_dir.name) / "site.db"
        with closing(sqlite3.connect(self.database)) as connection:
            with connection:
                connection.executescript(
                    """
                    CREATE TABLE enterprises (enterprise_id TEXT PRIMARY KEY);
                    CREATE TABLE managed_stores (
                        managed_store_id TEXT PRIMARY KEY, enterprise_id TEXT
                    );
                    CREATE TABLE departments (
                        department_id TEXT PRIMARY KEY, enterprise_id TEXT,
                        managed_store_id TEXT, department_type TEXT,
                        effective_from TEXT
                    );
                    CREATE TABLE team (id INTEGER PRIMARY KEY, store_id INTEGER);
                    CREATE TABLE team_member (
                        id INTEGER PRIMARY KEY, team_id INTEGER, tech_number TEXT,
                        daily_production_objective REAL, dpo_calculation_mode TEXT,
                        hist_frh_total REAL, hist_days_in_period INTEGER,
                        hist_training_days INTEGER, hist_vacation_days INTEGER,
                        expected_lift_percent REAL
                    );
                    CREATE TABLE schedule_entry (
                        id INTEGER PRIMARY KEY, team_member_id INTEGER,
                        schedule_type TEXT, date TEXT
                    );
                    CREATE TABLE production_objective_memo (
                        id INTEGER PRIMARY KEY, change_date TEXT
                    );
                    CREATE TABLE daily_metrics (
                        id INTEGER PRIMARY KEY, store_id INTEGER, date TEXT,
                        today_appts INTEGER, appt_7_day INTEGER, cp_ros_mtd INTEGER
                    );
                    CREATE TABLE repair_order (
                        id INTEGER PRIMARY KEY, store_id INTEGER, created_at TEXT
                    );
                    CREATE TABLE work_log (
                        id INTEGER PRIMARY KEY, team_member_id INTEGER, date TEXT,
                        ro_number TEXT, flat_rate_hours REAL
                    );
                    CREATE TABLE true_potential_evidence_packs (
                        true_potential_evidence_pack_id TEXT PRIMARY KEY,
                        enterprise_id TEXT, managed_store_id TEXT,
                        department_id TEXT, period_start TEXT, period_end TEXT,
                        observed_at TEXT, demand_status TEXT,
                        supported_demand_frh REAL, dpo_governance_status TEXT,
                        snapshot_json TEXT, source_trace_json TEXT,
                        limitations_json TEXT, content_hash TEXT,
                        created_at TEXT, updated_at TEXT, version INTEGER,
                        UNIQUE (enterprise_id, content_hash)
                    );
                    INSERT INTO enterprises VALUES ('enterprise-1');
                    INSERT INTO managed_stores VALUES ('store-1', 'enterprise-1');
                    INSERT INTO departments VALUES (
                        'department-1', 'enterprise-1', 'store-1', 'service',
                        '2026-01-01'
                    );
                    INSERT INTO team VALUES (1, 1);
                    INSERT INTO team_member VALUES (
                        10, 1, '100', 8.0, 'manual', 80.0, 10, 0, 0, 100.0
                    );
                    INSERT INTO schedule_entry VALUES (
                        1, 10, 'WORK', '2026-04-01'
                    );
                    INSERT INTO daily_metrics VALUES (
                        1, 1, '2026-04-01', 20, 100, NULL
                    );
                    INSERT INTO repair_order VALUES (1, 1, '2026-04-01 12:00:00');
                    INSERT INTO work_log VALUES (1, 10, '2026-04-01', 'RO-1', 6.0);
                    """
                )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_retrospective_pack_preserves_missing_authority(self) -> None:
        pack = build_evidence_pack(
            self.database, date(2026, 4, 1), date(2026, 4, 30)
        )
        self.assertEqual(pack["demand_status"], "unavailable")
        self.assertIsNone(pack["supported_demand_frh"])
        self.assertEqual(pack["dpo_governance_status"], "unverified_legacy")
        self.assertEqual(pack["technicians"][0]["authority_status"], "unverified_legacy")

        first_id, first_created = persist_evidence_pack(self.database, pack)
        second_id, second_created = persist_evidence_pack(self.database, pack)
        self.assertTrue(first_created)
        self.assertFalse(second_created)
        self.assertEqual(first_id, second_id)


if __name__ == "__main__":
    unittest.main()

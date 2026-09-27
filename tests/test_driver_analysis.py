from __future__ import annotations

import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import date
from pathlib import Path

from mi_v5.vertical_slice.driver_analysis import analyze_period_drivers


class DriverAnalysisTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = Path(self.temp_dir.name) / "site.db"
        with closing(sqlite3.connect(self.database)) as connection:
            connection.executescript(
                """
                CREATE TABLE team (id INTEGER PRIMARY KEY, store_id INTEGER);
                CREATE TABLE team_member (
                    id INTEGER PRIMARY KEY, team_id INTEGER, tech_number TEXT
                );
                CREATE TABLE work_log (
                    id INTEGER PRIMARY KEY, team_member_id INTEGER, date TEXT,
                    ro_number TEXT, flat_rate_hours REAL
                );
                CREATE TABLE daily_metrics (
                    id INTEGER PRIMARY KEY, store_id INTEGER, date TEXT,
                    total_gross REAL, labor_gross REAL, parts_gross REAL,
                    sublet_gross REAL, cp_ros_mtd INTEGER
                );
                CREATE TABLE user (id INTEGER PRIMARY KEY, store_id INTEGER);
                CREATE TABLE financial_inputs (
                    id INTEGER PRIMARY KEY, user_id INTEGER,
                    cp_effective_labor_rate REAL, effective_labor_rate REAL,
                    cp_parts_to_labor_ratio REAL, parts_to_labor_ratio REAL,
                    cp_labor_margin REAL, labor_margin REAL,
                    cp_parts_margin REAL, parts_margin REAL
                );
                INSERT INTO team VALUES (1, 1);
                INSERT INTO team_member VALUES (10, 1, '100');
                INSERT INTO team_member VALUES (11, 1, '101');
                INSERT INTO work_log VALUES (1, 10, '2026-04-01', 'RO-1', 2.0);
                INSERT INTO work_log VALUES (2, 10, '2026-04-01', 'RO-1', 1.0);
                INSERT INTO work_log VALUES (3, 11, '2026-04-02', 'RO-2', 5.0);
                INSERT INTO daily_metrics VALUES (
                    1, 1, '2026-04-02', 1000.0, 600.0, 400.0, 0.0, 2
                );
                INSERT INTO user VALUES (1, 1);
                INSERT INTO financial_inputs VALUES (
                    1, 1, 100.0, NULL, 1.0, NULL, 0.5, NULL, 0.4, NULL
                );
                """
            )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_decomposes_observed_drivers_without_enabling_correction(self) -> None:
        result = analyze_period_drivers(
            self.database, date(2026, 4, 1), date(2026, 4, 30)
        )
        self.assertEqual(result["production"]["actual_frh"], 8.0)
        self.assertEqual(result["production"]["ro_count"], 2)
        self.assertEqual(result["production"]["frh_per_ro"], 4.0)
        self.assertEqual(result["observed_economics"]["gross_per_cp_ro"], 500.0)
        self.assertEqual(
            result["configured_economic_assumptions"]["estimated_gp_per_frh"],
            90.0,
        )
        self.assertFalse(result["causal_boundary"]["correction_allowed"])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from datetime import date, datetime
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock, Mock, patch


def technician_row(**changes):
    row = {
        "id": 1,
        "tech_number": "100",
        "daily_production_objective": 9.5,
        "dpo_calculation_mode": "manual",
        "hist_frh_total": 80.0,
        "hist_days_in_period": 10,
        "hist_training_days": 0,
        "hist_vacation_days": 0,
        "expected_lift_percent": 100.0,
    }
    row.update(changes)
    return row


class PostgresDPOPreviewTests(unittest.TestCase):
    def setUp(self) -> None:
        # Import only this script, with a fake driver even if psycopg2 is installed.
        self.driver = ModuleType("psycopg2")
        extras = ModuleType("psycopg2.extras")
        extras.RealDictCursor = object()
        path = (
            Path(__file__).resolve().parents[1]
            / "scripts" / "preview_v5_postgres_dpo.py"
        )
        spec = importlib.util.spec_from_file_location("dpo_preview_under_test", path)
        self.module = importlib.util.module_from_spec(spec)
        with patch.dict(
            sys.modules, {"psycopg2": self.driver, "psycopg2.extras": extras}
        ):
            spec.loader.exec_module(self.module)

    def _preview(
        self, *, rows=None, database="dpo_v5_beta", revision="e82cd3516d34",
        missing_scope=False, employees=0, records=0,
        effective_from=date(2026, 10, 13),
    ):
        self.connection = MagicMock()
        self.cursor = MagicMock()
        self.cursor.__enter__.return_value = self.cursor
        self.connection.cursor.return_value = self.cursor
        self.driver.connect = Mock(return_value=self.connection)
        self.cursor.fetchone.side_effect = [
            {"name": database},
            {"version_num": revision},
            None if missing_scope else {
                "enterprise_id": "enterprise-1",
                "managed_store_id": "store-1",
                "department_id": "department-1",
            },
            {"n": employees},
            {"n": records},
        ]
        self.cursor.fetchall.return_value = (
            [technician_row()] if rows is None else rows
        )
        with patch.object(self.module, "datetime") as clock:
            clock.now.return_value = datetime(2026, 10, 12)
            return self.module.preview(
                host="unused", port=5432, dbname="dpo_v5_beta", user="unused",
                expected_database="dpo_v5_beta", legacy_store_id=2,
                effective_from=effective_from,
            )

    def test_default_inputs_are_visible_with_cautious_advisory(self) -> None:
        result = self._preview(employees=1)
        technician = result["technicians"][0]
        self.assertEqual(technician["calculation_inputs"], {
            "hist_frh_total": 80.0,
            "hist_days_in_period": 10,
            "hist_training_days": 0,
            "hist_vacation_days": 0,
            "expected_lift_percent": 100.0,
        })
        self.assertEqual(technician["productive_days"], 10)
        self.assertEqual(technician["calculated_comparison"], 8.0)
        self.assertEqual(technician["manual_minus_calculated"], 1.5)
        self.assertEqual(len(technician["calculation_warnings"]), 1)
        warning = technician["calculation_warnings"][0]
        self.assertIn("80/10/0/0/100", warning)
        self.assertIn("provenance is unverified", warning)
        self.assertIn("does not prove fabricated history", warning)
        self.assertEqual(result["blocking_issues"], [])
        json.dumps(result)

    def test_nondefault_inputs_keep_existing_calculation(self) -> None:
        row = technician_row(
            hist_frh_total=120.0, hist_days_in_period=12,
            hist_training_days=1, hist_vacation_days=1,
            expected_lift_percent=110.0, daily_production_objective=10.0,
        )
        technician = self._preview(rows=[row])["technicians"][0]
        self.assertEqual(technician["productive_days"], 10)
        self.assertEqual(technician["calculated_comparison"], 13.2)
        self.assertEqual(technician["manual_minus_calculated"], -3.2)
        self.assertEqual(technician["calculation_warnings"], [])
        for key, value in technician["calculation_inputs"].items():
            self.assertEqual(value, row[key])

    def test_nondefault_history_calculating_eight_is_not_flagged(self) -> None:
        row = technician_row(hist_frh_total=160.0, hist_days_in_period=20)
        technician = self._preview(rows=[row])["technicians"][0]
        self.assertEqual(technician["calculated_comparison"], 8.0)
        self.assertEqual(technician["calculation_warnings"], [])

    def test_calculation_and_difference_keep_four_decimal_precision(self) -> None:
        row = technician_row(
            hist_frh_total=82.0, hist_days_in_period=6,
            hist_training_days=1, hist_vacation_days=2,
            expected_lift_percent=110.0,
        )
        technician = self._preview(rows=[row])["technicians"][0]
        self.assertEqual(technician["calculated_comparison"], 30.0667)
        self.assertEqual(technician["manual_minus_calculated"], -20.5667)

    def test_missing_or_nonpositive_productive_days_remain_blocked(self) -> None:
        cases = [
            (None, None, None, 0),
            (0, 0, 0, 0),
            (1, 1, 0, 0),
            (10, 6, 5, -1),
        ]
        for period, training, vacation, productive in cases:
            with self.subTest(period=period, training=training, vacation=vacation):
                row = technician_row(
                    hist_days_in_period=period, hist_training_days=training,
                    hist_vacation_days=vacation,
                )
                result = self._preview(rows=[row])
                technician = result["technicians"][0]
                inputs = technician["calculation_inputs"]
                self.assertEqual(inputs["hist_days_in_period"], period)
                self.assertEqual(inputs["hist_training_days"], training)
                self.assertEqual(inputs["hist_vacation_days"], vacation)
                self.assertEqual(technician["productive_days"], productive)
                self.assertEqual(technician["calculated_comparison"], 0.0)
                self.assertEqual(technician["manual_minus_calculated"], 9.5)
                self.assertEqual(technician["calculation_warnings"], [])
                self.assertIn(
                    "Technician 1 lacks usable calculation history",
                    result["blocking_issues"],
                )
                json.dumps(result)

    def test_raw_missing_or_zero_lift_preserves_existing_fallback(self) -> None:
        for lift in (None, 0.0):
            with self.subTest(lift=lift):
                row = technician_row(expected_lift_percent=lift)
                technician = self._preview(rows=[row])["technicians"][0]
                self.assertEqual(
                    technician["calculation_inputs"]["expected_lift_percent"],
                    lift,
                )
                self.assertEqual(technician["calculated_comparison"], 8.0)
                self.assertEqual(technician["calculation_warnings"], [])

    def test_preview_remains_readonly_without_authority(self) -> None:
        for mode in ("manual", "calculated"):
            with self.subTest(mode=mode):
                result = self._preview(rows=[technician_row(dpo_calculation_mode=mode)])
                self.connection.set_session.assert_called_once_with(
                    readonly=True, autocommit=False
                )
                self.connection.close.assert_called_once_with()
                self.connection.commit.assert_not_called()
                self.assertTrue(all(
                    call.args[0].lstrip().upper().startswith("SELECT ")
                    for call in self.cursor.execute.call_args_list
                ))
                self.assertEqual(result["mode"], "preview_only")
                self.assertFalse(result["authority_created"])
                self.assertFalse(result["historical_dpo_verified"])
                self.assertEqual(result["canonical_employee_count"], 0)
                self.assertEqual(result["existing_governed_records"], 0)
                self.assertIn(
                    "No canonical Employee exists to approve DPO authority",
                    result["blocking_issues"],
                )
                self.assertEqual(
                    result["technicians"][0]["requires_override_review"],
                    mode != "calculated",
                )

    def test_wrong_database_stops_before_other_queries(self) -> None:
        with self.assertRaisesRegex(ValueError, "Expected database"):
            self._preview(database="operational_database")
        self.assertEqual(self.cursor.execute.call_count, 1)
        self.cursor.fetchall.assert_not_called()
        self.connection.close.assert_called_once_with()
        self.connection.commit.assert_not_called()

    def test_wrong_migration_stops_before_source_queries(self) -> None:
        with self.assertRaisesRegex(ValueError, "V5 migration head required"):
            self._preview(revision="old-revision")
        self.assertEqual(self.cursor.execute.call_count, 2)
        self.cursor.fetchall.assert_not_called()
        self.connection.close.assert_called_once_with()
        self.connection.commit.assert_not_called()

    def test_missing_scope_still_blocks_preview(self) -> None:
        with self.assertRaisesRegex(ValueError, "Service scope is missing"):
            self._preview(missing_scope=True)
        self.assertEqual(self.cursor.execute.call_count, 3)
        self.cursor.fetchall.assert_not_called()
        self.connection.close.assert_called_once_with()

    def test_past_effective_date_never_calls_driver(self) -> None:
        with self.assertRaisesRegex(ValueError, "must be prospective"):
            self._preview(effective_from=date(2026, 10, 11))
        self.driver.connect.assert_not_called()

    def test_no_active_technicians_still_reports_missing_evidence(self) -> None:
        result = self._preview(rows=[])
        self.assertEqual(result["technicians"], [])
        self.assertEqual(result["technician_count"], 0)
        self.assertIn("No active technicians found", result["blocking_issues"])
        self.assertFalse(result["authority_created"])
        self.assertFalse(result["historical_dpo_verified"])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import copy
import importlib.util
import unittest
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID
from unittest.mock import MagicMock, Mock, patch

from mi_v5.schema_versions import ASSIGNMENT_REVISION
from mi_v5.vertical_slice.dpo_approval import (
    assignment_issues, build_proposal, source_fingerprint,
)

NOW = datetime(2026, 10, 13, 17, tzinfo=timezone.utc)
START = "2026-10-10T07:00:00+00:00"
END = "2026-10-20T07:00:00+00:00"


def uid(number):
    return str(UUID(int=number))


def snapshot():
    # Synthetic records only: these are not proposed identity/authority rows.
    return {
        "database": "dpo_v5_beta", "migration": ASSIGNMENT_REVISION,
        "scope": {
            "enterprise_id": uid(1), "managed_store_id": uid(2),
            "department_id": uid(3), "enterprise_name": "AutoNation",
            "store_name": "Honda Renton", "store_code": "HONDA_RENTON",
            "external_reference": "legacy_managed_store:2",
            "department_code": "SERVICE", "department_type": "service",
            "enterprise_status": "active", "enterprise_retired_at": None,
            "store_status": "active", "store_retired_at": None,
            "department_status": "active", "department_retired_at": None,
            "department_effective_from": START, "department_effective_to": None,
        },
        "employees": [{
            "employee_id": uid(4), "enterprise_id": uid(1),
            "status": "active", "retired_at": None,
        }],
        "roles": [{
            "role_id": uid(5), "enterprise_id": uid(1), "status": "active",
            "retired_at": None, "effective_from": START, "effective_to": None,
        }],
        "assignments": [{
            "assignment_id": uid(6), "enterprise_id": uid(1),
            "employee_id": uid(4), "role_id": uid(5), "department_id": uid(3),
            "status": "active", "is_primary": True,
            "effective_from": START, "effective_to": END,
            "source_reference": "fixture-only-persona-review", "created_by_id": uid(4),
        }],
        "capabilities": [{
            "capability_id": uid(7), "enterprise_id": uid(1),
            "key": "dpo.authorize", "status": "active", "retired_at": None,
            "effective_from": START, "effective_to": None,
        }],
        "role_grants": [{
            "role_capability_id": uid(8), "enterprise_id": uid(1),
            "role_id": uid(5), "capability_id": uid(7),
            "effective_from": START, "effective_to": None,
        }],
        "technicians": [{
            "id": 1, "tech_number": "FIXTURE-1",
            "daily_production_objective": 9.5, "dpo_calculation_mode": "manual",
            "hist_frh_total": 80.0, "hist_days_in_period": 10,
            "hist_training_days": 0, "hist_vacation_days": 0,
            "expected_lift_percent": 100.0,
        }],
        "existing_dpos": [],
    }


def review(data):
    return {
        "enterprise_id": uid(1), "managed_store_id": uid(2),
        "department_id": uid(3), "authorized_by_id": uid(4),
        "role_id": uid(5), "assignment_id": uid(6), "role_capability_id": uid(8),
        "effective_from": "2026-10-14", "effective_to": None,
        "source_fingerprint": source_fingerprint(data),
        "approval_reference": "fixture-only-DPO-review", "authority_status": "provisional",
        "approvals": [{
            "legacy_team_member_id": 1, "approved_value": 9.5,
            "reason": "Explicit synthetic fixture override approval",
        }],
    }


class AssignmentGovernanceTests(unittest.TestCase):
    def setUp(self):
        self.data = snapshot()
        self.review = review(self.data)

    def proposal(self):
        return build_proposal(self.data, self.review, now=NOW)

    def assertBlocked(self, text):
        result = self.proposal()
        self.assertTrue(result["blocked"], result)
        self.assertTrue(any(text in issue for issue in result["blocking_issues"]),
                        result["blocking_issues"])
        self.assertFalse(result["apply_available"])
        self.assertTrue(all(item["planned_change"]["operation"] == "blocked"
                            for item in result["proposed_records"]))
        return result

    def test_complete_review_is_only_a_non_executable_proposal(self):
        result = self.proposal()
        self.assertFalse(result["blocked"], result["blocking_issues"])
        self.assertFalse(result["apply_available"])
        self.assertFalse(result["authority_created"])
        self.assertFalse(result["historical_dpo_verified"])
        self.assertTrue(result["future_apply_requires_transactional_revalidation"])
        item = result["proposed_records"][0]
        self.assertEqual(item["planned_change"], {"operation": "insert"})
        self.assertEqual(item["record"]["dpo_value"], 9.5)
        self.assertTrue(item["record"]["is_override"])
        self.assertEqual(item["record"]["calculated_dpo"], 8.0)
        self.assertIsNone(item["record"]["technician_dpo_record_id"])
        self.assertIsNone(item["record"]["created_at"])
        self.assertEqual(item["record"]["authority_status"], "provisional")
        self.assertIn("assignment=", item["record"]["source_reference"])
        self.assertTrue(item["calculation_warnings"])

    def test_empty_review_does_not_fill_human_values_reasons_or_dates(self):
        self.review = {}
        result = self.assertBlocked("explicit positive reviewed value")
        record = result["proposed_records"][0]["record"]
        for key in ("dpo_value", "authorization_reason", "effective_from",
                    "authorized_by_id", "source_reference"):
            self.assertIsNone(record[key])

    def test_wrong_tenant_scope_and_entities_are_rejected(self):
        for location in ("review", "employee", "role", "assignment", "grant", "capability"):
            with self.subTest(location=location):
                self.setUp()
                rows = {
                    "employee": "employees", "role": "roles", "assignment": "assignments",
                    "grant": "role_grants", "capability": "capabilities",
                }
                if location == "review":
                    self.review["enterprise_id"] = uid(10)
                else:
                    self.data[rows[location]][0]["enterprise_id"] = uid(10)
                self.assertTrue(self.proposal()["blocked"])

    def test_wrong_store_labels_or_department_bindings_are_rejected(self):
        self.data["scope"]["store_code"] = "OTHER"
        with self.assertRaisesRegex(ValueError, "Exact Honda Renton"):
            self.proposal()
        self.setUp()
        self.review["managed_store_id"] = uid(10)
        self.assertBlocked("reviewed managed_store_id")
        self.setUp()
        self.data["assignments"][0]["department_id"] = uid(10)
        self.assertBlocked("does not authorize")

    def test_wrong_role_or_capability_is_rejected(self):
        for field in ("assignment-role", "grant-role", "capability-key", "capability-id"):
            with self.subTest(field=field):
                self.setUp()
                if field == "assignment-role":
                    self.data["assignments"][0]["role_id"] = uid(10)
                elif field == "grant-role":
                    self.data["role_grants"][0]["role_id"] = uid(10)
                elif field == "capability-key":
                    self.data["capabilities"][0]["key"] = "dpo.read"
                else:
                    self.data["role_grants"][0]["capability_id"] = uid(10)
                self.assertTrue(self.proposal()["blocked"])

    def test_no_implicit_authority_from_staffing_or_review_supplied_records(self):
        self.data["assignments"] = []
        self.data["employee_assignments"] = [{
            "employee_id": uid(4), "position_id": uid(11), "is_managerial": True,
        }]
        self.review["assignments"] = snapshot()["assignments"]
        self.assertBlocked("Canonical Assignment requires")

    def test_lifecycle_and_retirement_fail_closed(self):
        for key in ("employees", "roles", "capabilities", "assignments"):
            with self.subTest(key=key):
                self.setUp()
                self.data[key][0]["status"] = "pending"
                self.assertTrue(self.proposal()["blocked"])
        for key in ("employees", "roles", "capabilities"):
            with self.subTest(retired=key):
                self.setUp()
                self.data[key][0]["retired_at"] = START
                self.assertTrue(self.proposal()["blocked"])
        self.setUp()
        self.data["scope"]["store_status"] = "inactive"
        self.assertBlocked("Canonical store")

    def test_missing_retirement_or_period_metadata_is_not_assumed_active(self):
        del self.data["employees"][0]["retired_at"]
        self.assertBlocked("Employee must be active")
        self.setUp()
        del self.data["role_grants"][0]["effective_to"]
        self.assertBlocked("invalid timezone-aware period")

    def test_future_start_exact_end_and_unbounded_test_assignment_are_rejected(self):
        for key in ("assignments", "roles", "capabilities", "role_grants"):
            for change in ("future-start", "exact-end"):
                with self.subTest(key=key, change=change):
                    self.setUp()
                    self.data[key][0]["effective_from" if change == "future-start"
                                      else "effective_to"] = (
                        "2026-10-14T07:00:00+00:00" if change == "future-start"
                        else NOW.isoformat()
                    )
                    self.assertTrue(self.proposal()["blocked"])
        self.setUp()
        self.data["assignments"][0]["effective_to"] = None
        self.assertBlocked("explicit bounded end")

    def test_effective_end_equal_start_and_naive_timestamps_are_invalid(self):
        self.data["assignments"][0]["effective_to"] = START
        self.assertBlocked("valid explicit effective period")
        self.setUp()
        self.data["assignments"][0]["effective_from"] = "2026-10-10T07:00:00"
        self.assertBlocked("valid explicit effective period")
        with self.assertRaises(ValueError):
            build_proposal(snapshot(), review(snapshot()), now=NOW.replace(tzinfo=None))

    def test_prospective_date_uses_los_angeles_day_and_role_window(self):
        self.review["effective_from"] = "2026-10-12"
        self.assertBlocked("prospective")
        self.setUp()
        self.review["effective_from"] = "2026-10-20"
        self.assertBlocked("Assignment is outside")
        # 00:30 UTC is still October 13 in Los Angeles.
        self.setUp()
        self.review["effective_from"] = "2026-10-13"
        result = build_proposal(
            self.data, self.review,
            now=datetime(2026, 10, 14, 0, 30, tzinfo=timezone.utc),
        )
        self.assertFalse(result["blocked"], result["blocking_issues"])

    def test_assignment_source_and_audit_actor_are_required(self):
        self.data["assignments"][0]["source_reference"] = None
        self.assertBlocked("reviewed source")
        self.setUp()
        self.data["assignments"][0]["created_by_id"] = uid(10)
        self.assertBlocked("audit actor requires")

    def test_primary_overlap_is_role_context_scoped_including_finite_intervals(self):
        other = copy.deepcopy(self.data["assignments"][0])
        other.update(assignment_id=uid(10), employee_id=uid(11))
        self.data["assignments"].append(other)
        self.assertBlocked("Overlapping exclusive primary")
        other["department_id"] = uid(12)
        result = self.proposal()
        self.assertFalse(result["blocked"], result["blocking_issues"])

    def test_published_assignment_changes_and_duplicate_identity_are_rejected(self):
        original = self.data["assignments"][0]
        changed = copy.deepcopy(original)
        changed["source_reference"] = "replacement"
        self.assertIn("Published Assignment requires append-only correction",
                      assignment_issues(changed, [original]))
        duplicate = copy.deepcopy(original)
        duplicate["assignment_id"] = uid(10)
        self.assertIn("Duplicate Assignment effective identity",
                      assignment_issues(duplicate, [original]))

    def test_stale_source_and_revoked_grant_block_a_previously_complete_review(self):
        self.assertFalse(self.proposal()["blocked"])
        self.data["technicians"][0]["hist_frh_total"] = 90.0
        self.assertBlocked("source fingerprint")
        self.setUp()
        self.data["role_grants"][0]["effective_to"] = NOW.isoformat()
        self.assertBlocked("grant is outside")

    def test_duplicate_unknown_approvals_and_unreviewed_values_are_rejected(self):
        self.review["approvals"].append(copy.deepcopy(self.review["approvals"][0]))
        self.assertBlocked("unique explicit")
        self.setUp()
        self.review["approvals"].append({
            "legacy_team_member_id": 999, "approved_value": 8.0, "reason": "fixture",
        })
        self.assertBlocked("outside the active store")
        for value in (None, True, 0, -1, float("inf"), float("nan")):
            with self.subTest(value=value):
                self.setUp()
                self.review["approvals"][0]["approved_value"] = value
                self.assertBlocked("positive reviewed value")
        self.setUp()
        self.review["approvals"][0]["reason"] = 123
        self.assertBlocked("explicit human reason")

    def test_no_verified_status_apply_flag_or_disguised_calculated_override(self):
        self.review["authority_status"] = "verified"
        self.assertBlocked("provisional")
        self.setUp()
        self.review["apply"] = True
        self.assertBlocked("Apply is unsupported")
        self.setUp()
        self.data["technicians"][0]["dpo_calculation_mode"] = "calculated"
        self.review["source_fingerprint"] = source_fingerprint(self.data)
        self.assertBlocked("disguise an override")

    def test_idempotent_record_and_conflicting_same_date_are_classified(self):
        record = copy.deepcopy(self.proposal()["proposed_records"][0]["record"])
        record["technician_dpo_record_id"] = uid(9)
        self.data["existing_dpos"] = [record]
        self.assertEqual(self.proposal()["proposed_records"][0]["planned_change"],
                         {"operation": "unchanged"})
        record["dpo_value"] = 8.5
        self.assertBlocked("Conflicting existing DPO")

    def test_supersession_plan_retains_prior_record_and_moves_forward(self):
        record = copy.deepcopy(self.proposal()["proposed_records"][0]["record"])
        record.update(technician_dpo_record_id=uid(9), effective_from="2026-10-12")
        self.data["existing_dpos"] = [record]
        result = self.proposal()
        self.assertEqual(result["proposed_records"][0]["planned_change"], {
            "operation": "supersede", "prior_record_id": uid(9),
            "close_prior_at": "2026-10-13",
        })
        self.assertIsNone(record["effective_to"])
        record["effective_from"] = "2026-10-15"
        self.assertBlocked("move forward")

    def test_matching_open_dpo_cannot_hide_later_bounded_history(self):
        matching = copy.deepcopy(self.proposal()["proposed_records"][0]["record"])
        matching["technician_dpo_record_id"] = uid(9)
        later = dict(matching, technician_dpo_record_id=uid(10),
                     effective_from="2026-10-15", effective_to="2026-10-16")
        self.data["existing_dpos"] = [matching, later]
        self.assertBlocked("history overlaps")

    def test_matching_bounded_dpo_cannot_hide_earlier_open_history(self):
        self.review["effective_to"] = "2026-10-16"
        matching = copy.deepcopy(self.proposal()["proposed_records"][0]["record"])
        matching["technician_dpo_record_id"] = uid(9)
        earlier = dict(matching, technician_dpo_record_id=uid(10),
                       effective_from="2026-10-12", effective_to=None)
        self.data["existing_dpos"] = [matching, earlier]
        self.assertBlocked("history overlaps")

    def test_matching_open_dpo_cannot_hide_another_open_record(self):
        matching = copy.deepcopy(self.proposal()["proposed_records"][0]["record"])
        matching["technician_dpo_record_id"] = uid(9)
        earlier = dict(matching, technician_dpo_record_id=uid(10),
                       effective_from="2026-10-12")
        self.data["existing_dpos"] = [matching, earlier]
        self.assertBlocked("Ambiguous current DPO")

    def test_matching_dpo_with_closed_nonoverlapping_history_remains_unchanged(self):
        matching = copy.deepcopy(self.proposal()["proposed_records"][0]["record"])
        matching["technician_dpo_record_id"] = uid(9)
        earlier = dict(matching, technician_dpo_record_id=uid(10),
                       effective_from="2026-10-12", effective_to="2026-10-13")
        self.data["existing_dpos"] = [matching, earlier]
        result = self.proposal()
        self.assertFalse(result["blocked"], result["blocking_issues"])
        self.assertEqual(result["proposed_records"][0]["planned_change"],
                         {"operation": "unchanged"})

    def test_matching_bounded_dpo_with_nonoverlapping_later_history_remains_unchanged(self):
        self.review["effective_to"] = "2026-10-16"
        matching = copy.deepcopy(self.proposal()["proposed_records"][0]["record"])
        matching["technician_dpo_record_id"] = uid(9)
        later = dict(matching, technician_dpo_record_id=uid(10),
                     effective_from="2026-10-17", effective_to="2026-10-18")
        self.data["existing_dpos"] = [matching, later]
        result = self.proposal()
        self.assertFalse(result["blocked"], result["blocking_issues"])
        self.assertEqual(result["proposed_records"][0]["planned_change"],
                         {"operation": "unchanged"})

    def test_existing_dpo_scope_mismatch_and_bounded_overlap_are_rejected(self):
        record = copy.deepcopy(self.proposal()["proposed_records"][0]["record"])
        record.update(technician_dpo_record_id=uid(9), effective_from="2026-10-12")
        self.data["existing_dpos"] = [record]
        record["managed_store_id"] = uid(10)
        self.assertBlocked("another tenant/store/department")
        record["managed_store_id"] = uid(2)
        record["effective_to"] = "2026-10-14"
        self.assertBlocked("bounded DPO overlaps")

    def test_employee_count_is_not_multiplied_by_authority_rows(self):
        extra = copy.deepcopy(self.data["role_grants"][0])
        extra["role_capability_id"] = uid(10)
        self.data["role_grants"].append(extra)
        self.assertEqual(self.proposal()["canonical_employee_count"], 1)

    def test_twenty_unreviewed_candidates_create_no_identity_or_authority(self):
        original = self.data["technicians"][0]
        self.data["technicians"] = [
            dict(original, id=number, tech_number=f"FIXTURE-{number}")
            for number in range(1, 21)
        ]
        for key in ("employees", "roles", "assignments", "capabilities", "role_grants"):
            self.data[key] = []
        self.review = {}
        result = self.proposal()
        self.assertTrue(result["blocked"])
        self.assertEqual(result["technician_count"], 20)
        self.assertEqual(result["canonical_employee_count"], 0)
        self.assertFalse(result["authority_created"])
        self.assertTrue(all(item["record"]["dpo_value"] is None
                            for item in result["proposed_records"]))


class ReadOnlyGovernanceReaderTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / "scripts" / \
            "preview_v5_postgres_governance.py"
        spec = importlib.util.spec_from_file_location("governance_reader_under_test", path)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.data = snapshot()
        self.connection = MagicMock()
        self.cursor = MagicMock()
        self.cursor.__enter__.return_value = self.cursor
        self.connection.cursor.return_value = self.cursor
        self.factory = Mock(return_value=self.connection)

    def read(self, *, actual="dpo_v5_beta", revision=ASSIGNMENT_REVISION,
             scopes=None, legacy="Honda Renton", dbname="dpo_v5_beta"):
        self.cursor.fetchone.side_effect = [
            {"name": actual}, {"version_num": revision},
            None if legacy is None else {"name": legacy},
        ]
        self.cursor.fetchall.side_effect = [
            [self.data["scope"]] if scopes is None else scopes,
            *[self.data[key] for key in (
                "employees", "roles", "assignments", "capabilities",
                "role_grants", "existing_dpos", "technicians",
            )],
        ]
        return self.module.read_snapshot(
            "unused", 5432, dbname, "unused",
            connection_factory=self.factory, cursor_factory=object(),
        )

    def test_reader_uses_only_selects_in_readonly_transaction(self):
        actual = self.read()
        self.assertEqual(actual, self.data)
        self.connection.set_session.assert_called_once_with(
            readonly=True, autocommit=False, isolation_level="REPEATABLE READ"
        )
        self.connection.close.assert_called_once_with()
        self.connection.commit.assert_not_called()
        self.assertTrue(all(
            call.args[0].lstrip().upper().startswith("SELECT ")
            for call in self.cursor.execute.call_args_list
        ))

    def test_live_database_name_is_rejected_before_connection(self):
        with self.assertRaisesRegex(ValueError, "isolated"):
            self.read(dbname="dpo4db")
        self.factory.assert_not_called()

    def test_connected_database_and_old_unknown_revision_fail_before_authority_reads(self):
        for actual, revision in (
            ("dpo_beta", ASSIGNMENT_REVISION),
            ("dpo_v5_beta", "e82cd3516d34"),
            ("dpo_v5_beta", "unreviewed-head"),
        ):
            with self.subTest(actual=actual, revision=revision):
                self.setUp()
                with self.assertRaises(ValueError):
                    self.read(actual=actual, revision=revision)
                self.assertLessEqual(self.cursor.execute.call_count, 2)
                self.cursor.fetchall.assert_not_called()
                self.connection.close.assert_called_once_with()
                self.connection.commit.assert_not_called()

    def test_missing_or_ambiguous_service_scope_is_never_selected_arbitrarily(self):
        for scopes in ([], [self.data["scope"], self.data["scope"]]):
            with self.subTest(count=len(scopes)):
                self.setUp()
                with self.assertRaisesRegex(ValueError, "missing or ambiguous"):
                    self.read(scopes=scopes)
                self.assertEqual(self.cursor.execute.call_count, 3)
                self.connection.close.assert_called_once_with()

    def test_wrong_legacy_store_stops_before_authority_queries(self):
        with self.assertRaisesRegex(ValueError, "not Honda Renton"):
            self.read(legacy="Another Store")
        self.assertEqual(self.cursor.execute.call_count, 4)

    def test_cli_has_no_apply_mode(self):
        with patch.object(self.module.sys, "argv", [
            "preview", "--host", "unused", "--port", "5432",
            "--dbname", "dpo_v5_beta", "--user", "unused", "--apply",
        ]), patch.object(self.module, "read_snapshot") as read:
            with self.assertRaises(SystemExit) as caught:
                self.module.main()
            self.assertEqual(caught.exception.code, 2)
            read.assert_not_called()


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import date, datetime, timezone
from pathlib import Path

from mi_v5.vertical_slice.contracts import (
    EconomicInputs,
    SourceReference,
    StorePeriodEvidence,
    TechnicianPotentialInput,
)
from mi_v5.vertical_slice.decision_store import (
    DecisionStoreError,
    SQLiteDecisionStore,
)
from mi_v5.vertical_slice.engine import evaluate_case


SCHEMA = """
CREATE TABLE employees (
    enterprise_id TEXT NOT NULL,
    employee_id TEXT NOT NULL,
    PRIMARY KEY (employee_id),
    UNIQUE (enterprise_id, employee_id)
);
CREATE TABLE recommendation_outputs (
    recommendation_output_id TEXT PRIMARY KEY,
    enterprise_id TEXT NOT NULL,
    managed_store_id TEXT NOT NULL,
    department_id TEXT NOT NULL,
    case_id TEXT NOT NULL,
    generated_at TEXT NOT NULL,
    proposed_response TEXT NOT NULL,
    expected_effect TEXT NOT NULL,
    attention_class TEXT NOT NULL,
    assumptions_json TEXT NOT NULL,
    evidence_trace_json TEXT NOT NULL,
    snapshot_json TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    version INTEGER NOT NULL,
    UNIQUE (enterprise_id, content_hash)
);
CREATE TABLE management_decisions (
    management_decision_id TEXT PRIMARY KEY,
    enterprise_id TEXT NOT NULL,
    recommendation_output_id TEXT,
    managed_store_id TEXT NOT NULL,
    department_id TEXT NOT NULL,
    accountable_owner_id TEXT NOT NULL,
    decided_at TEXT NOT NULL,
    disposition TEXT NOT NULL,
    decision_statement TEXT NOT NULL,
    rationale TEXT NOT NULL,
    original_context_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    version INTEGER NOT NULL,
    UNIQUE (enterprise_id, recommendation_output_id)
);
CREATE TABLE management_actions (
    management_action_id TEXT PRIMARY KEY,
    enterprise_id TEXT NOT NULL,
    management_decision_id TEXT NOT NULL,
    owner_id TEXT NOT NULL,
    action_text TEXT NOT NULL,
    completion_condition TEXT NOT NULL,
    due_at TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    version INTEGER NOT NULL
);
"""


def evidence() -> StorePeriodEvidence:
    days = tuple(date(2026, 4, day) for day in range(1, 4))
    return StorePeriodEvidence(
        enterprise_id="enterprise-1",
        managed_store_id="store-1",
        department_id="department-1",
        legacy_store_id=1,
        period_start=days[0],
        period_end=days[-1],
        extracted_at=datetime(2026, 4, 4, tzinfo=timezone.utc),
        technicians=(
            TechnicianPotentialInput(
                technician_id=1,
                dpo=8.0,
                dpo_mode="manual",
                scheduled_dates=days,
                history_frh=None,
                history_days=None,
                expected_lift_percent=None,
            ),
        ),
        production_dates=days[:2],
        scheduled_operating_dates=days,
        actual_frh=16.0,
        repair_order_count=8,
        actual_mtd_gross=2_500.0,
        actual_mtd_gross_date=days[1],
        supported_demand_frh=None,
        economics=EconomicInputs(150.0, 0.8, 80.0, 40.0, "customer_pay"),
        accountable_owner_id="manager-1",
        accountable_position_id="position-1",
        sources=(SourceReference("work_log", "test-v1", 8),),
    )


class DecisionStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = Path(self.temp_dir.name) / "decision.db"
        with closing(sqlite3.connect(self.database)) as connection:
            with connection:
                connection.executescript(SCHEMA)
                connection.execute(
                    "INSERT INTO employees (enterprise_id, employee_id) VALUES (?, ?)",
                    ("enterprise-1", "manager-1"),
                )
        self.store = SQLiteDecisionStore(self.database)
        self.evidence = evidence()
        self.result = evaluate_case(self.evidence)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_recommendation_is_advisory_and_idempotent(self) -> None:
        first = self.store.record_recommendation(self.evidence, self.result)
        second = self.store.record_recommendation(self.evidence, self.result)

        self.assertEqual(first, second)
        with closing(sqlite3.connect(self.database)) as connection:
            recommendation_count = connection.execute(
                "SELECT COUNT(*) FROM recommendation_outputs"
            ).fetchone()[0]
            decision_count = connection.execute(
                "SELECT COUNT(*) FROM management_decisions"
            ).fetchone()[0]
        self.assertEqual(recommendation_count, 1)
        self.assertEqual(decision_count, 0)

    def test_rejected_decision_cannot_create_action(self) -> None:
        recommendation_id = self.store.record_recommendation(
            self.evidence, self.result
        )
        decision_id = self.store.record_decision(
            recommendation_id,
            "reject",
            "manager-1",
            "Do not proceed.",
            "Source reconciliation already established complete coverage.",
        )

        with self.assertRaisesRegex(
            DecisionStoreError, "rejected or deferred"
        ):
            self.store.record_action(
                decision_id,
                None,
                "Reconcile evidence.",
                "Every scheduled date is reconciled.",
                datetime(2026, 4, 5, tzinfo=timezone.utc),
            )

    def test_recommendation_cannot_silently_receive_a_second_decision(self) -> None:
        recommendation_id = self.store.record_recommendation(
            self.evidence, self.result
        )
        self.store.record_decision(
            recommendation_id,
            "defer",
            "manager-1",
            "Wait for source reconciliation.",
            "The current evidence window is incomplete.",
        )

        with self.assertRaisesRegex(
            DecisionStoreError, "already has a Management Decision"
        ):
            self.store.record_decision(
                recommendation_id,
                "accept",
                "manager-1",
                "Proceed with correction.",
                "The evidence is now considered sufficient.",
            )

    def test_accepted_decision_creates_planned_action(self) -> None:
        recommendation_id = self.store.record_recommendation(
            self.evidence, self.result
        )
        decision_id = self.store.record_decision(
            recommendation_id,
            "accept",
            "manager-1",
            "Reconcile the uncovered dates.",
            "The evidence gap blocks a fair performance judgment.",
        )
        action_id = self.store.record_action(
            decision_id,
            None,
            "Reconcile production evidence with the source system.",
            "Every scheduled date has production or governed zero evidence.",
            datetime(2026, 4, 5, tzinfo=timezone.utc),
        )

        with closing(sqlite3.connect(self.database)) as connection:
            row = connection.execute(
                "SELECT status, owner_id FROM management_actions "
                "WHERE management_action_id = ?",
                (action_id,),
            ).fetchone()
        self.assertEqual(row, ("planned", "manager-1"))


if __name__ == "__main__":
    unittest.main()

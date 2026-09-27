"""Append-only SQLite persistence for the first accountable decision loop."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .contracts import StorePeriodEvidence, VerticalSliceResult

REQUIRED_TABLES = {
    "recommendation_outputs",
    "management_decisions",
    "management_actions",
}
DECISION_DISPOSITIONS = {"accept", "modify", "reject", "defer"}
ACTIONABLE_DISPOSITIONS = {"accept", "modify"}


class DecisionStoreError(ValueError):
    """Raised when a decision-loop invariant would be violated."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _required_text(value: str, label: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise DecisionStoreError(f"{label} is required")
    return normalized


class SQLiteDecisionStore:
    """Persist explicit human choices without mutating source evidence."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def assert_schema(self) -> None:
        with closing(self._connect()) as connection:
            existing = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
        missing = REQUIRED_TABLES - existing
        if missing:
            names = ", ".join(sorted(missing))
            raise DecisionStoreError(
                f"Decision-loop schema is missing: {names}. Run 'flask db upgrade'."
            )

    def record_recommendation(
        self,
        evidence: StorePeriodEvidence,
        result: VerticalSliceResult,
    ) -> str:
        """Store one advisory output idempotently by governed content hash."""

        self.assert_schema()
        snapshot = result.to_dict()
        snapshot_json = json.dumps(snapshot, sort_keys=True, separators=(",", ":"))
        content_hash = hashlib.sha256(snapshot_json.encode("utf-8")).hexdigest()
        recommendation_id = uuid4().hex
        timestamp = _now()
        assumptions = {
            "method_version": result.true_potential.method_version,
            "validation_status": result.true_potential.validation_status.value,
            "limitations": list(result.true_potential.limitations),
        }

        with closing(self._connect()) as connection:
            with connection:
                existing = connection.execute(
                    """
                    SELECT recommendation_output_id
                    FROM recommendation_outputs
                    WHERE enterprise_id = ? AND content_hash = ?
                    """,
                    (evidence.enterprise_id, content_hash),
                ).fetchone()
                if existing:
                    return str(existing["recommendation_output_id"])

                connection.execute(
                    """
                    INSERT INTO recommendation_outputs (
                        recommendation_output_id, enterprise_id, managed_store_id,
                        department_id, case_id, generated_at, proposed_response,
                        expected_effect, attention_class, assumptions_json,
                        evidence_trace_json, snapshot_json, content_hash, status,
                        created_at, updated_at, version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, 1)
                    """,
                    (
                        recommendation_id,
                        evidence.enterprise_id,
                        evidence.managed_store_id,
                        evidence.department_id,
                        result.case_id,
                        timestamp,
                        result.management_position.recommended_intervention,
                        result.management_position.expected_outcome,
                        result.management_position.attention.value,
                        json.dumps(assumptions, sort_keys=True),
                        json.dumps(result.trace, sort_keys=True),
                        snapshot_json,
                        content_hash,
                        timestamp,
                        timestamp,
                    ),
                )
        return recommendation_id

    def record_decision(
        self,
        recommendation_id: str,
        disposition: str,
        accountable_owner_id: str,
        decision_statement: str,
        rationale: str,
    ) -> str:
        """Append an explicit human Decision; never infer one from a recommendation."""

        self.assert_schema()
        if disposition not in DECISION_DISPOSITIONS:
            allowed = ", ".join(sorted(DECISION_DISPOSITIONS))
            raise DecisionStoreError(f"disposition must be one of: {allowed}")
        statement = _required_text(decision_statement, "decision_statement")
        reason = _required_text(rationale, "rationale")
        owner_id = _required_text(accountable_owner_id, "accountable_owner_id")
        decision_id = uuid4().hex
        timestamp = _now()

        with closing(self._connect()) as connection:
            with connection:
                recommendation = connection.execute(
                    """
                    SELECT * FROM recommendation_outputs
                    WHERE recommendation_output_id = ? AND status = 'active'
                    """,
                    (recommendation_id,),
                ).fetchone()
                if recommendation is None:
                    raise DecisionStoreError("active recommendation was not found")
                prior_decision = connection.execute(
                    """
                    SELECT management_decision_id
                    FROM management_decisions
                    WHERE enterprise_id = ? AND recommendation_output_id = ?
                    """,
                    (recommendation["enterprise_id"], recommendation_id),
                ).fetchone()
                if prior_decision is not None:
                    raise DecisionStoreError(
                        "this Recommendation Output already has a Management Decision"
                    )
                owner = connection.execute(
                    """
                    SELECT 1 FROM employees
                    WHERE enterprise_id = ? AND employee_id = ?
                    """,
                    (recommendation["enterprise_id"], owner_id),
                ).fetchone()
                if owner is None:
                    raise DecisionStoreError(
                        "accountable owner is not an Employee in the recommendation's Enterprise"
                    )

                context = {
                    "recommendation_output_id": recommendation_id,
                    "case_id": recommendation["case_id"],
                    "content_hash": recommendation["content_hash"],
                    "snapshot": json.loads(recommendation["snapshot_json"]),
                }
                connection.execute(
                    """
                    INSERT INTO management_decisions (
                        management_decision_id, enterprise_id,
                        recommendation_output_id, managed_store_id, department_id,
                        accountable_owner_id, decided_at, disposition,
                        decision_statement, rationale, original_context_json,
                        created_at, updated_at, version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                    """,
                    (
                        decision_id,
                        recommendation["enterprise_id"],
                        recommendation_id,
                        recommendation["managed_store_id"],
                        recommendation["department_id"],
                        owner_id,
                        timestamp,
                        disposition,
                        statement,
                        reason,
                        json.dumps(context, sort_keys=True),
                        timestamp,
                        timestamp,
                    ),
                )
        return decision_id

    def record_action(
        self,
        decision_id: str,
        owner_id: str | None,
        action_text: str,
        completion_condition: str,
        due_at: datetime,
    ) -> str:
        """Create an Action only for an explicitly actionable human Decision."""

        self.assert_schema()
        action = _required_text(action_text, "action_text")
        completion = _required_text(
            completion_condition, "completion_condition"
        )
        if due_at.tzinfo is None:
            raise DecisionStoreError("due_at must include a timezone")
        action_id = uuid4().hex
        timestamp = _now()

        with closing(self._connect()) as connection:
            with connection:
                decision = connection.execute(
                    """
                    SELECT * FROM management_decisions
                    WHERE management_decision_id = ?
                    """,
                    (decision_id,),
                ).fetchone()
                if decision is None:
                    raise DecisionStoreError("management decision was not found")
                if decision["disposition"] not in ACTIONABLE_DISPOSITIONS:
                    raise DecisionStoreError(
                        "a rejected or deferred Decision cannot create an Action"
                    )
                resolved_owner = owner_id or decision["accountable_owner_id"]
                owner = connection.execute(
                    """
                    SELECT 1 FROM employees
                    WHERE enterprise_id = ? AND employee_id = ?
                    """,
                    (decision["enterprise_id"], resolved_owner),
                ).fetchone()
                if owner is None:
                    raise DecisionStoreError(
                        "action owner is not an Employee in the Decision's Enterprise"
                    )

                connection.execute(
                    """
                    INSERT INTO management_actions (
                        management_action_id, enterprise_id,
                        management_decision_id, owner_id, action_text,
                        completion_condition, due_at, status,
                        created_at, updated_at, version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'planned', ?, ?, 1)
                    """,
                    (
                        action_id,
                        decision["enterprise_id"],
                        decision_id,
                        resolved_owner,
                        action,
                        completion,
                        due_at.isoformat(),
                        timestamp,
                        timestamp,
                    ),
                )
        return action_id

    def get_recommendation(self, recommendation_id: str) -> dict[str, object]:
        self.assert_schema()
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT * FROM recommendation_outputs WHERE recommendation_output_id = ?",
                (recommendation_id,),
            ).fetchone()
        if row is None:
            raise DecisionStoreError("recommendation was not found")
        return dict(row)

    def get_decision(self, decision_id: str) -> dict[str, object]:
        self.assert_schema()
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT * FROM management_decisions WHERE management_decision_id = ?",
                (decision_id,),
            ).fetchone()
        if row is None:
            raise DecisionStoreError("management decision was not found")
        return dict(row)

"""Append-only SQLite persistence for the first accountable decision loop."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import closing
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import uuid4

from .contracts import StorePeriodEvidence, VerticalSliceResult

REQUIRED_TABLES = {
    "execution_evidence",
    "recommendation_outputs",
    "management_decisions",
    "management_actions",
    "outcomes",
    "validations",
}
DECISION_DISPOSITIONS = {"accept", "modify", "reject", "defer"}
ACTIONABLE_DISPOSITIONS = {"accept", "modify"}
EVIDENCE_TYPES = {
    "approved_exception",
    "document",
    "observation",
    "source_reconciliation",
    "system_record",
}
VALIDATION_RESULTS = {
    "achieved",
    "partially_achieved",
    "not_achieved",
    "inconclusive",
    "invalidated",
}
OUTCOME_CLASSIFICATIONS = {
    "favorable",
    "neutral",
    "unfavorable",
    "inconclusive",
}


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

                prior = connection.execute(
                    """
                    SELECT recommendation_output_id
                    FROM recommendation_outputs
                    WHERE enterprise_id = ? AND case_id = ?
                    ORDER BY generated_at DESC, created_at DESC
                    LIMIT 1
                    """,
                    (evidence.enterprise_id, result.case_id),
                ).fetchone()
                supersedes_id = (
                    str(prior["recommendation_output_id"]) if prior else None
                )
                if supersedes_id:
                    connection.execute(
                        """
                        UPDATE recommendation_outputs
                        SET status = 'superseded', updated_at = ?, version = version + 1
                        WHERE enterprise_id = ?
                          AND recommendation_output_id = ?
                        """,
                        (timestamp, evidence.enterprise_id, supersedes_id),
                    )

                connection.execute(
                    """
                    INSERT INTO recommendation_outputs (
                        recommendation_output_id, enterprise_id, managed_store_id,
                        department_id, supersedes_recommendation_output_id,
                        case_id, generated_at, proposed_response,
                        expected_effect, attention_class, assumptions_json,
                        evidence_trace_json, snapshot_json, content_hash, status,
                        created_at, updated_at, version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, 1)
                    """,
                    (
                        recommendation_id,
                        evidence.enterprise_id,
                        evidence.managed_store_id,
                        evidence.department_id,
                        supersedes_id,
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
                    WHERE recommendation_output_id = ?
                    """,
                    (recommendation_id,),
                ).fetchone()
                if recommendation is None:
                    raise DecisionStoreError("recommendation was not found")
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
                if recommendation["status"] != "active":
                    raise DecisionStoreError(
                        "only an active Recommendation Output may receive a Decision"
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
                connection.execute(
                    """
                    UPDATE recommendation_outputs
                    SET status = 'resolved', updated_at = ?, version = version + 1
                    WHERE enterprise_id = ? AND recommendation_output_id = ?
                    """,
                    (timestamp, recommendation["enterprise_id"], recommendation_id),
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

    def get_action(self, action_id: str) -> dict[str, object]:
        self.assert_schema()
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT * FROM management_actions WHERE management_action_id = ?",
                (action_id,),
            ).fetchone()
        if row is None:
            raise DecisionStoreError("management action was not found")
        return dict(row)

    def record_execution_evidence(
        self,
        action_id: str,
        recorded_by_id: str,
        evidence_type: str,
        description: str,
        source_reference: str,
        occurred_at: datetime,
        payload: dict[str, object] | None = None,
        claims_completion: bool = False,
    ) -> str:
        """Append proof and audit the resulting Action status transition."""

        self.assert_schema()
        if evidence_type not in EVIDENCE_TYPES:
            allowed = ", ".join(sorted(EVIDENCE_TYPES))
            raise DecisionStoreError(f"evidence_type must be one of: {allowed}")
        if occurred_at.tzinfo is None:
            raise DecisionStoreError("occurred_at must include a timezone")
        recorder = _required_text(recorded_by_id, "recorded_by_id")
        detail = _required_text(description, "description")
        source = _required_text(source_reference, "source_reference")
        evidence_id = uuid4().hex
        timestamp = _now()

        with closing(self._connect()) as connection:
            with connection:
                action = connection.execute(
                    "SELECT * FROM management_actions WHERE management_action_id = ?",
                    (action_id,),
                ).fetchone()
                if action is None:
                    raise DecisionStoreError("management action was not found")
                if action["status"] == "cancelled":
                    raise DecisionStoreError("a cancelled Action cannot receive execution evidence")
                employee = connection.execute(
                    "SELECT 1 FROM employees WHERE enterprise_id = ? AND employee_id = ?",
                    (action["enterprise_id"], recorder),
                ).fetchone()
                if employee is None:
                    raise DecisionStoreError(
                        "evidence recorder is not an Employee in the Action's Enterprise"
                    )

                prior_status = str(action["status"])
                if claims_completion:
                    resulting_status = "completed"
                elif prior_status == "planned":
                    resulting_status = "in_progress"
                else:
                    resulting_status = prior_status

                connection.execute(
                    """
                    INSERT INTO execution_evidence (
                        execution_evidence_id, enterprise_id,
                        management_action_id, recorded_by_id, occurred_at,
                        evidence_type, description, source_reference,
                        payload_json, claims_completion, prior_action_status,
                        resulting_action_status, created_at, updated_at, version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                    """,
                    (
                        evidence_id,
                        action["enterprise_id"],
                        action_id,
                        recorder,
                        occurred_at.isoformat(),
                        evidence_type,
                        detail,
                        source,
                        json.dumps(payload or {}, sort_keys=True),
                        int(claims_completion),
                        prior_status,
                        resulting_status,
                        timestamp,
                        timestamp,
                    ),
                )
                if resulting_status != prior_status:
                    connection.execute(
                        """
                        UPDATE management_actions
                        SET status = ?, updated_at = ?, version = version + 1
                        WHERE management_action_id = ?
                        """,
                        (resulting_status, timestamp, action_id),
                    )
        return evidence_id

    def record_validation(
        self,
        action_id: str,
        validator_id: str,
        evaluation_target: str,
        expected_result: str,
        observed_result: str,
        period_start: date,
        period_end: date,
        method: str,
        result: str,
        confidence: str,
        supporting_evidence_ids: list[str],
    ) -> str:
        """Append a governed comparison only after execution is evidenced."""

        self.assert_schema()
        if result not in VALIDATION_RESULTS:
            allowed = ", ".join(sorted(VALIDATION_RESULTS))
            raise DecisionStoreError(f"validation result must be one of: {allowed}")
        if period_end < period_start:
            raise DecisionStoreError("validation period end cannot precede its start")
        if not supporting_evidence_ids:
            raise DecisionStoreError("Validation requires supporting Execution Evidence")
        validator = _required_text(validator_id, "validator_id")
        target = _required_text(evaluation_target, "evaluation_target")
        expected = _required_text(expected_result, "expected_result")
        observed = _required_text(observed_result, "observed_result")
        validation_method = _required_text(method, "method")
        confidence_value = _required_text(confidence, "confidence").lower()
        if confidence_value not in {"low", "medium", "high"}:
            raise DecisionStoreError("confidence must be low, medium, or high")
        validation_id = uuid4().hex
        timestamp = _now()

        with closing(self._connect()) as connection:
            with connection:
                action = connection.execute(
                    "SELECT * FROM management_actions WHERE management_action_id = ?",
                    (action_id,),
                ).fetchone()
                if action is None:
                    raise DecisionStoreError("management action was not found")
                if action["status"] != "completed":
                    raise DecisionStoreError(
                        "Validation requires a completed Action with Execution Evidence"
                    )
                employee = connection.execute(
                    "SELECT 1 FROM employees WHERE enterprise_id = ? AND employee_id = ?",
                    (action["enterprise_id"], validator),
                ).fetchone()
                if employee is None:
                    raise DecisionStoreError(
                        "validator is not an Employee in the Action's Enterprise"
                    )
                evidence_rows = connection.execute(
                    f"""
                    SELECT execution_evidence_id FROM execution_evidence
                    WHERE enterprise_id = ? AND management_action_id = ?
                      AND execution_evidence_id IN ({','.join('?' for _ in supporting_evidence_ids)})
                    """,
                    (action["enterprise_id"], action_id, *supporting_evidence_ids),
                ).fetchall()
                found_ids = {str(row["execution_evidence_id"]) for row in evidence_rows}
                if found_ids != set(supporting_evidence_ids):
                    raise DecisionStoreError(
                        "all supporting evidence must belong to the validated Action"
                    )

                connection.execute(
                    """
                    INSERT INTO validations (
                        validation_id, enterprise_id, management_action_id,
                        validator_id, validated_at, evaluation_target,
                        expected_result, observed_result, evaluation_period_start,
                        evaluation_period_end, method, result, confidence,
                        supporting_evidence_json, created_at, updated_at, version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                    """,
                    (
                        validation_id,
                        action["enterprise_id"],
                        action_id,
                        validator,
                        timestamp,
                        target,
                        expected,
                        observed,
                        period_start.isoformat(),
                        period_end.isoformat(),
                        validation_method,
                        result,
                        confidence_value,
                        json.dumps(sorted(found_ids)),
                        timestamp,
                        timestamp,
                    ),
                )
        return validation_id

    def record_outcome(
        self,
        validation_id: str,
        recorded_by_id: str,
        observed_result: str,
        expected_actual_variance: str,
        classification: str,
        period_start: date,
        period_end: date,
        supporting_evidence_ids: list[str],
    ) -> str:
        """Append an observed Outcome without making a causal claim."""

        self.assert_schema()
        if classification not in OUTCOME_CLASSIFICATIONS:
            allowed = ", ".join(sorted(OUTCOME_CLASSIFICATIONS))
            raise DecisionStoreError(f"classification must be one of: {allowed}")
        if period_end < period_start:
            raise DecisionStoreError("Outcome period end cannot precede its start")
        if not supporting_evidence_ids:
            raise DecisionStoreError("Outcome requires supporting Execution Evidence")
        recorder = _required_text(recorded_by_id, "recorded_by_id")
        observed = _required_text(observed_result, "observed_result")
        variance = _required_text(expected_actual_variance, "expected_actual_variance")
        outcome_id = uuid4().hex
        timestamp = _now()

        with closing(self._connect()) as connection:
            with connection:
                validation = connection.execute(
                    """
                    SELECT v.*, a.management_decision_id
                    FROM validations v
                    JOIN management_actions a
                      ON a.enterprise_id = v.enterprise_id
                     AND a.management_action_id = v.management_action_id
                    WHERE v.validation_id = ?
                    """,
                    (validation_id,),
                ).fetchone()
                if validation is None:
                    raise DecisionStoreError("Validation was not found")
                employee = connection.execute(
                    "SELECT 1 FROM employees WHERE enterprise_id = ? AND employee_id = ?",
                    (validation["enterprise_id"], recorder),
                ).fetchone()
                if employee is None:
                    raise DecisionStoreError(
                        "Outcome recorder is not an Employee in the Validation's Enterprise"
                    )
                evidence_rows = connection.execute(
                    f"""
                    SELECT execution_evidence_id FROM execution_evidence
                    WHERE enterprise_id = ? AND management_action_id = ?
                      AND execution_evidence_id IN ({','.join('?' for _ in supporting_evidence_ids)})
                    """,
                    (
                        validation["enterprise_id"],
                        validation["management_action_id"],
                        *supporting_evidence_ids,
                    ),
                ).fetchall()
                found_ids = {str(row["execution_evidence_id"]) for row in evidence_rows}
                if found_ids != set(supporting_evidence_ids):
                    raise DecisionStoreError(
                        "all supporting evidence must belong to the validated Action"
                    )

                connection.execute(
                    """
                    INSERT INTO outcomes (
                        outcome_id, enterprise_id, management_decision_id,
                        management_action_id, validation_id, recorded_by_id,
                        observed_at, period_start, period_end, observed_result,
                        expected_actual_variance, classification,
                        supporting_evidence_json, association_only,
                        created_at, updated_at, version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, 1)
                    """,
                    (
                        outcome_id,
                        validation["enterprise_id"],
                        validation["management_decision_id"],
                        validation["management_action_id"],
                        validation_id,
                        recorder,
                        timestamp,
                        period_start.isoformat(),
                        period_end.isoformat(),
                        observed,
                        variance,
                        classification,
                        json.dumps(sorted(found_ids)),
                        timestamp,
                        timestamp,
                    ),
                )
        return outcome_id

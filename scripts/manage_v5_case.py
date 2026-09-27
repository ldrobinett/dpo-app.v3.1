"""Operate the governed MI path from Recommendation through observed Outcome."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mi_v5.vertical_slice import evaluate_case, load_store_period
from mi_v5.vertical_slice.decision_store import SQLiteDecisionStore


def _database_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--database", type=Path, default=Path("instance/site.db")
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    recommend = subparsers.add_parser(
        "recommend", help="Evaluate and persist an advisory Recommendation Output"
    )
    _database_argument(recommend)
    recommend.add_argument("--store-id", type=int, default=1)
    recommend.add_argument(
        "--period-start", type=date.fromisoformat, required=True
    )
    recommend.add_argument(
        "--period-end", type=date.fromisoformat, required=True
    )

    decide = subparsers.add_parser(
        "decide", help="Record an explicit accountable human Decision"
    )
    _database_argument(decide)
    decide.add_argument("--recommendation-id", required=True)
    decide.add_argument(
        "--disposition",
        required=True,
        choices=("accept", "modify", "reject", "defer"),
    )
    decide.add_argument(
        "--owner-id",
        default="recommended",
        help="Employee UUID or 'recommended' to use the routed owner",
    )
    decide.add_argument("--statement", required=True)
    decide.add_argument("--rationale", required=True)

    action = subparsers.add_parser(
        "action", help="Create accountable work from an accepted/modified Decision"
    )
    _database_argument(action)
    action.add_argument("--decision-id", required=True)
    action.add_argument(
        "--owner-id",
        help="Employee UUID; defaults to the Decision's accountable owner",
    )
    action.add_argument("--action", required=True)
    action.add_argument("--completion-condition", required=True)
    action.add_argument(
        "--due-at",
        type=datetime.fromisoformat,
        required=True,
        help="ISO timestamp including timezone, for example 2026-09-27T12:00:00-07:00",
    )

    evidence = subparsers.add_parser(
        "evidence", help="Append proof of Action execution"
    )
    _database_argument(evidence)
    evidence.add_argument("--action-id", required=True)
    evidence.add_argument(
        "--recorded-by-id",
        default="owner",
        help="Employee UUID or 'owner' to use the Action owner",
    )
    evidence.add_argument(
        "--type",
        required=True,
        choices=(
            "source_reconciliation",
            "system_record",
            "document",
            "observation",
            "approved_exception",
        ),
    )
    evidence.add_argument("--description", required=True)
    evidence.add_argument("--source-reference", required=True)
    evidence.add_argument(
        "--occurred-at", type=datetime.fromisoformat, required=True
    )
    evidence.add_argument("--payload-json", default="{}")
    evidence.add_argument("--completes-action", action="store_true")

    validate = subparsers.add_parser(
        "validate", help="Compare an Action's expected and observed result"
    )
    _database_argument(validate)
    validate.add_argument("--action-id", required=True)
    validate.add_argument(
        "--validator-id",
        default="owner",
        help="Employee UUID or 'owner' to use the Action owner",
    )
    validate.add_argument("--evaluation-target", required=True)
    validate.add_argument("--expected-result", required=True)
    validate.add_argument("--observed-result", required=True)
    validate.add_argument("--period-start", type=date.fromisoformat, required=True)
    validate.add_argument("--period-end", type=date.fromisoformat, required=True)
    validate.add_argument("--method", required=True)
    validate.add_argument(
        "--result",
        required=True,
        choices=(
            "achieved",
            "partially_achieved",
            "not_achieved",
            "inconclusive",
            "invalidated",
        ),
    )
    validate.add_argument(
        "--confidence", required=True, choices=("low", "medium", "high")
    )
    validate.add_argument("--evidence-id", action="append", required=True)

    outcome = subparsers.add_parser(
        "outcome", help="Record an observed, non-causal Outcome"
    )
    _database_argument(outcome)
    outcome.add_argument("--validation-id", required=True)
    outcome.add_argument("--recorded-by-id", required=True)
    outcome.add_argument("--observed-result", required=True)
    outcome.add_argument("--expected-actual-variance", required=True)
    outcome.add_argument(
        "--classification",
        required=True,
        choices=("favorable", "neutral", "unfavorable", "inconclusive"),
    )
    outcome.add_argument("--period-start", type=date.fromisoformat, required=True)
    outcome.add_argument("--period-end", type=date.fromisoformat, required=True)
    outcome.add_argument("--evidence-id", action="append", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    store = SQLiteDecisionStore(args.database)

    if args.command == "recommend":
        evidence = load_store_period(
            args.database,
            period_start=args.period_start,
            period_end=args.period_end,
            legacy_store_id=args.store_id,
        )
        result = evaluate_case(evidence)
        recommendation_id = store.record_recommendation(evidence, result)
        print(
            json.dumps(
                {
                    "recommendation_output_id": recommendation_id,
                    "case_id": result.case_id,
                    "attention": result.management_position.attention.value,
                    "position": result.management_position.position,
                    "proposed_response": result.management_position.recommended_intervention,
                    "recommended_owner_id": result.management_position.owner_id,
                    "decision_required": result.management_position.decision_required,
                },
                indent=2,
            )
        )
        return 0

    if args.command == "decide":
        recommendation = store.get_recommendation(args.recommendation_id)
        snapshot = json.loads(str(recommendation["snapshot_json"]))
        owner_id = args.owner_id
        if owner_id == "recommended":
            owner_id = snapshot["management_position"]["owner_id"]
        if not owner_id:
            raise ValueError(
                "No recommended owner is available; provide --owner-id explicitly"
            )
        decision_id = store.record_decision(
            recommendation_id=args.recommendation_id,
            disposition=args.disposition,
            accountable_owner_id=owner_id,
            decision_statement=args.statement,
            rationale=args.rationale,
        )
        print(
            json.dumps(
                {
                    "management_decision_id": decision_id,
                    "recommendation_output_id": args.recommendation_id,
                    "disposition": args.disposition,
                    "accountable_owner_id": owner_id,
                },
                indent=2,
            )
        )
        return 0

    if args.command == "action":
        decision = store.get_decision(args.decision_id)
        action_id = store.record_action(
            decision_id=args.decision_id,
            owner_id=args.owner_id,
            action_text=args.action,
            completion_condition=args.completion_condition,
            due_at=args.due_at,
        )
        print(
            json.dumps(
                {
                    "management_action_id": action_id,
                    "management_decision_id": args.decision_id,
                    "owner_id": args.owner_id or decision["accountable_owner_id"],
                    "status": "planned",
                    "due_at": args.due_at.isoformat(),
                },
                indent=2,
            )
        )
        return 0

    if args.command == "evidence":
        action = store.get_action(args.action_id)
        recorder = (
            action["owner_id"]
            if args.recorded_by_id == "owner"
            else args.recorded_by_id
        )
        evidence_id = store.record_execution_evidence(
            action_id=args.action_id,
            recorded_by_id=str(recorder),
            evidence_type=args.type,
            description=args.description,
            source_reference=args.source_reference,
            occurred_at=args.occurred_at,
            payload=json.loads(args.payload_json),
            claims_completion=args.completes_action,
        )
        resulting_action = store.get_action(args.action_id)
        print(
            json.dumps(
                {
                    "execution_evidence_id": evidence_id,
                    "management_action_id": args.action_id,
                    "action_status": resulting_action["status"],
                    "claims_completion": args.completes_action,
                },
                indent=2,
            )
        )
        return 0

    if args.command == "validate":
        action = store.get_action(args.action_id)
        validator = (
            action["owner_id"] if args.validator_id == "owner" else args.validator_id
        )
        validation_id = store.record_validation(
            action_id=args.action_id,
            validator_id=str(validator),
            evaluation_target=args.evaluation_target,
            expected_result=args.expected_result,
            observed_result=args.observed_result,
            period_start=args.period_start,
            period_end=args.period_end,
            method=args.method,
            result=args.result,
            confidence=args.confidence,
            supporting_evidence_ids=args.evidence_id,
        )
        print(
            json.dumps(
                {
                    "validation_id": validation_id,
                    "management_action_id": args.action_id,
                    "result": args.result,
                    "confidence": args.confidence,
                },
                indent=2,
            )
        )
        return 0

    outcome_id = store.record_outcome(
        validation_id=args.validation_id,
        recorded_by_id=args.recorded_by_id,
        observed_result=args.observed_result,
        expected_actual_variance=args.expected_actual_variance,
        classification=args.classification,
        period_start=args.period_start,
        period_end=args.period_end,
        supporting_evidence_ids=args.evidence_id,
    )
    print(
        json.dumps(
            {
                "outcome_id": outcome_id,
                "validation_id": args.validation_id,
                "classification": args.classification,
                "association_only": True,
                "organizational_learning_claimed": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

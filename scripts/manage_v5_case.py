"""Persist an advisory MI result, explicit human Decision, and Action."""

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


if __name__ == "__main__":
    raise SystemExit(main())

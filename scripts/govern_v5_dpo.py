"""Preview or authorize the current technician DPO set prospectively."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mi_v5.vertical_slice.dpo_governance import (
    apply_current_dpo_plan,
    build_current_dpo_plan,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=Path("instance/site.db"))
    parser.add_argument("--store-id", type=int, default=1)
    parser.add_argument("--effective-from", type=date.fromisoformat, required=True)
    parser.add_argument("--authorized-by-id", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument(
        "--authority-status",
        choices=("provisional", "verified"),
        default="provisional",
    )
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    plan = build_current_dpo_plan(
        args.database,
        args.effective_from,
        args.authorized_by_id,
        args.reason,
        legacy_store_id=args.store_id,
        authority_status=args.authority_status,
    )
    output = {
        "mode": "apply" if args.apply else "dry_run",
        "effective_from": plan["effective_from"],
        "authorized_by_id": plan["authorized_by_id"],
        "authority_status": plan["authority_status"],
        "technician_count": len(plan["technicians"]),
        "manual_override_count": sum(
            1 for item in plan["technicians"] if item["is_override"]
        ),
        "technicians": plan["technicians"],
        "blocked": bool(plan["blocking_issues"]),
        "blocking_issues": plan["blocking_issues"],
        "limitations": plan["limitations"],
    }
    if args.apply:
        output.update(apply_current_dpo_plan(args.database, plan))
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

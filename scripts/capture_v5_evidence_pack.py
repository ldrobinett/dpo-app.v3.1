"""Inspect and optionally retain the governed True Potential evidence state."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mi_v5.vertical_slice.evidence_pack import (
    build_evidence_pack,
    persist_evidence_pack,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=Path("instance/site.db"))
    parser.add_argument("--store-id", type=int, default=1)
    parser.add_argument("--period-start", type=date.fromisoformat, required=True)
    parser.add_argument("--period-end", type=date.fromisoformat, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    pack = build_evidence_pack(
        args.database, args.period_start, args.period_end, args.store_id
    )
    output = {
        "mode": "apply" if args.apply else "dry_run",
        "period_start": pack["period_start"],
        "period_end": pack["period_end"],
        "demand_status": pack["demand_status"],
        "supported_demand_frh": pack["supported_demand_frh"],
        "dpo_governance_status": pack["dpo_governance_status"],
        "technician_count": len(pack["technicians"]),
        "dpo_history_rows": pack["sources_checked"][
            "production_objective_memo_rows"
        ],
        "limitations": pack["limitations"],
        "content_hash": pack["content_hash"],
    }
    if args.apply:
        pack_id, created = persist_evidence_pack(args.database, pack)
        output["true_potential_evidence_pack_id"] = pack_id
        output["created"] = created
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

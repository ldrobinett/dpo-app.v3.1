"""Run Vertical Slice 1 against a read-only ProdTracker SQLite database."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mi_v5.vertical_slice import evaluate_case, load_store_period


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--database", type=Path, default=Path("instance/site.db")
    )
    parser.add_argument("--store-id", type=int, default=1)
    parser.add_argument(
        "--period-start", type=date.fromisoformat, required=True
    )
    parser.add_argument(
        "--period-end", type=date.fromisoformat, required=True
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    evidence = load_store_period(
        args.database,
        period_start=args.period_start,
        period_end=args.period_end,
        legacy_store_id=args.store_id,
    )
    result = evaluate_case(evidence)
    print(json.dumps(result.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

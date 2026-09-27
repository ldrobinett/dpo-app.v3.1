"""Decompose observed period drivers without asserting an unsupported cause."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mi_v5.vertical_slice.driver_analysis import analyze_period_drivers


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=Path("instance/site.db"))
    parser.add_argument("--store-id", type=int, default=1)
    parser.add_argument("--period-start", type=date.fromisoformat, required=True)
    parser.add_argument("--period-end", type=date.fromisoformat, required=True)
    args = parser.parse_args()
    result = analyze_period_drivers(
        args.database, args.period_start, args.period_end, args.store_id
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Dry-run and import a bounded CDK reconciliation export into legacy WorkLog."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class SourceRow:
    tech_number: str
    booked_date: date
    ro_number: str
    line_item: str
    actual_hours: float
    sold_hours: float

    @property
    def source_key(self) -> tuple[str, str, str, float, float]:
        return (
            self.booked_date.isoformat(),
            self.ro_number,
            self.line_item,
            round(self.actual_hours, 4),
            round(self.sold_hours, 4),
        )


def _parse_source(
    source_path: Path, period_start: date, period_end: date
) -> tuple[list[SourceRow], dict[str, int]]:
    rows: list[SourceRow] = []
    skipped = Counter()
    with source_path.open("r", encoding="latin-1", newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        for row in reader:
            if not row or not any(cell.strip() for cell in row):
                skipped["empty"] += 1
                continue
            if len(row) < 14:
                skipped["short"] += 1
                continue
            if not row[0].strip():
                skipped["missing_ro"] += 1
                continue
            try:
                booked_date = datetime.strptime(row[1].strip(), "%d%b%y").date()
            except ValueError:
                skipped["subtotal_or_invalid_date"] += 1
                continue
            if not period_start <= booked_date <= period_end:
                skipped["outside_period"] += 1
                continue
            try:
                actual_hours = float(row[12].strip() or 0.0)
                sold_hours = float(row[13].strip() or 0.0)
            except ValueError:
                skipped["invalid_hours"] += 1
                continue
            rows.append(
                SourceRow(
                    tech_number=row[4].strip(),
                    booked_date=booked_date,
                    ro_number=row[0].strip(),
                    line_item=row[5].strip(),
                    actual_hours=actual_hours,
                    sold_hours=sold_hours,
                )
            )
    return rows, dict(skipped)


def build_plan(
    database_path: Path,
    source_path: Path,
    store_id: int,
    period_start: date,
    period_end: date,
    excluded_techs: set[str],
    exclusion_reason: str,
) -> tuple[dict[str, object], list[tuple[SourceRow, int]]]:
    if period_end < period_start:
        raise ValueError("period_end must be on or after period_start")
    if excluded_techs and not exclusion_reason.strip():
        raise ValueError("an exclusion reason is required when technicians are excluded")

    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    source_rows, skipped = _parse_source(source_path, period_start, period_end)
    connection = sqlite3.connect(f"file:{database_path.resolve()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        tech_map = {
            str(row["tech_number"]).strip(): int(row["id"])
            for row in connection.execute(
                """
                SELECT tm.id, tm.tech_number
                FROM team_member tm
                JOIN team t ON t.id = tm.team_id
                WHERE t.store_id = ? AND tm.tech_number IS NOT NULL
                """,
                (store_id,),
            )
        }
        existing = Counter(
            (
                int(row["team_member_id"]),
                str(row["date"]),
                str(row["ro_number"] or ""),
                str(row["line_item"] or ""),
                round(float(row["actual_time"] or 0.0), 4),
                round(float(row["flat_rate_hours"] or 0.0), 4),
            )
            for row in connection.execute(
                """
                SELECT w.team_member_id, w.date, w.ro_number, w.line_item,
                       w.actual_time, w.flat_rate_hours
                FROM work_log w
                JOIN team_member tm ON tm.id = w.team_member_id
                JOIN team t ON t.id = tm.team_id
                WHERE t.store_id = ? AND w.date BETWEEN ? AND ?
                """,
                (store_id, period_start.isoformat(), period_end.isoformat()),
            )
        )
    finally:
        connection.close()

    excluded = defaultdict(lambda: {"rows": 0, "sold_hours": 0.0})
    unknown = defaultdict(lambda: {"rows": 0, "sold_hours": 0.0})
    candidates: list[tuple[SourceRow, int]] = []
    already_present = 0
    for row in source_rows:
        if row.tech_number in excluded_techs:
            excluded[row.tech_number]["rows"] += 1
            excluded[row.tech_number]["sold_hours"] += row.sold_hours
            continue
        team_member_id = tech_map.get(row.tech_number)
        if team_member_id is None:
            unknown[row.tech_number]["rows"] += 1
            unknown[row.tech_number]["sold_hours"] += row.sold_hours
            continue
        database_key = (team_member_id, *row.source_key)
        if existing[database_key] > 0:
            existing[database_key] -= 1
            already_present += 1
            continue
        candidates.append((row, team_member_id))

    def summarized(values: dict[str, dict[str, float]]) -> dict[str, object]:
        return {
            key: {
                "rows": int(value["rows"]),
                "sold_hours": round(value["sold_hours"], 2),
            }
            for key, value in sorted(values.items())
        }

    plan: dict[str, object] = {
        "source": {
            "path": str(source_path),
            "sha256": source_hash,
            "bytes": source_path.stat().st_size,
        },
        "scope": {
            "store_id": store_id,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
        },
        "parsed_target_rows": len(source_rows),
        "skipped": skipped,
        "excluded_technicians": summarized(excluded),
        "exclusion_reason": exclusion_reason if excluded else None,
        "unmapped_technicians": summarized(unknown),
        "already_present_rows": already_present,
        "proposed_insert_rows": len(candidates),
        "proposed_insert_sold_hours": round(
            sum(row.sold_hours for row, _ in candidates), 2
        ),
        "blocked": bool(unknown),
    }
    return plan, candidates


def apply_plan(
    database_path: Path,
    backup_path: Path,
    plan: dict[str, object],
    candidates: list[tuple[SourceRow, int]],
) -> None:
    if plan["blocked"]:
        raise ValueError("import is blocked by unmapped technicians")
    if backup_path.exists():
        raise FileExistsError(f"backup already exists: {backup_path}")
    if database_path.resolve() == backup_path.resolve():
        raise ValueError("backup path must differ from the database path")
    backup_path.parent.mkdir(parents=True, exist_ok=True)

    source_hash = str(plan["source"]["sha256"])
    timestamp = datetime.now(timezone.utc).isoformat()
    connection = sqlite3.connect(database_path)
    try:
        with sqlite3.connect(backup_path) as backup:
            connection.backup(backup)
        with connection:
            connection.executemany(
                """
                INSERT INTO work_log (
                    team_member_id, date, actual_time, ro_number, line_item,
                    flat_rate_hours, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        team_member_id,
                        row.booked_date.isoformat(),
                        row.actual_hours,
                        row.ro_number,
                        row.line_item,
                        row.sold_hours,
                        "Governed V5 reconciliation; "
                        f"source_sha256={source_hash}",
                    )
                    for row, team_member_id in candidates
                ],
            )
            connection.execute(
                """
                UPDATE managed_store
                SET tech_hours_audit_timestamp = ?
                WHERE id = ?
                """,
                (timestamp, plan["scope"]["store_id"]),
            )
    finally:
        connection.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=Path("instance/site.db"))
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--store-id", type=int, default=1)
    parser.add_argument("--period-start", type=date.fromisoformat, required=True)
    parser.add_argument("--period-end", type=date.fromisoformat, required=True)
    parser.add_argument("--exclude-tech", action="append", default=[])
    parser.add_argument("--exclusion-reason", default="")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--backup", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan, candidates = build_plan(
        args.database,
        args.source,
        args.store_id,
        args.period_start,
        args.period_end,
        set(args.exclude_tech),
        args.exclusion_reason,
    )
    plan["mode"] = "apply" if args.apply else "dry_run"
    if args.apply:
        if args.backup is None:
            raise ValueError("--backup is required with --apply")
        apply_plan(args.database, args.backup, plan, candidates)
        plan["backup"] = str(args.backup)
        plan["inserted_rows"] = len(candidates)
        plan["inserted_sold_hours"] = plan["proposed_insert_sold_hours"]
    print(json.dumps(plan, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

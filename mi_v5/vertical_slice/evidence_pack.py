"""Retain an immutable retrospective True Potential input assessment."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import closing
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import uuid4


def build_evidence_pack(
    database_path: str | Path,
    period_start: date,
    period_end: date,
    legacy_store_id: int = 1,
) -> dict[str, object]:
    if period_end < period_start:
        raise ValueError("period_end must be on or after period_start")
    path = Path(database_path)
    with closing(
        sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    ) as connection:
        connection.row_factory = sqlite3.Row
        scope = connection.execute(
            """
            SELECT e.enterprise_id, ms.managed_store_id, d.department_id
            FROM enterprises e
            JOIN managed_stores ms ON ms.enterprise_id = e.enterprise_id
            JOIN departments d
              ON d.enterprise_id = e.enterprise_id
             AND d.managed_store_id = ms.managed_store_id
            WHERE d.department_type = 'service'
            ORDER BY d.effective_from LIMIT 1
            """
        ).fetchone()
        if scope is None:
            raise ValueError("V5 Enterprise, Managed Store, and Service Department required")

        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

        technicians = [
            dict(row)
            for row in connection.execute(
                """
                SELECT tm.id AS legacy_team_member_id, tm.tech_number,
                       tm.daily_production_objective AS dpo,
                       tm.dpo_calculation_mode AS dpo_mode,
                       tm.hist_frh_total, tm.hist_days_in_period,
                       tm.hist_training_days, tm.hist_vacation_days,
                       tm.expected_lift_percent,
                       COUNT(se.id) AS scheduled_days
                FROM team_member tm
                JOIN team t ON t.id = tm.team_id
                JOIN schedule_entry se ON se.team_member_id = tm.id
                WHERE t.store_id = ? AND se.schedule_type = 'WORK'
                  AND se.date BETWEEN ? AND ?
                GROUP BY tm.id ORDER BY tm.id
                """,
                (legacy_store_id, period_start.isoformat(), period_end.isoformat()),
            )
        ]
        memo_count = connection.execute(
            "SELECT COUNT(*) FROM production_objective_memo"
        ).fetchone()[0]
        governed_dpo: dict[int, dict[str, object]] = {}
        if "technician_dpo_records" in tables:
            for row in connection.execute(
                """
                SELECT legacy_team_member_id, dpo_value, calculation_mode,
                       calculated_dpo, is_override, authority_status,
                       authorized_by_id, authorization_reason,
                       effective_from, effective_to, source_reference
                FROM technician_dpo_records
                WHERE enterprise_id = ? AND managed_store_id = ?
                  AND department_id = ? AND effective_from <= ?
                  AND (effective_to IS NULL OR effective_to >= ?)
                ORDER BY legacy_team_member_id, effective_from DESC
                """,
                (
                    scope["enterprise_id"], scope["managed_store_id"],
                    scope["department_id"], period_start.isoformat(),
                    period_end.isoformat(),
                ),
            ):
                governed_dpo.setdefault(int(row["legacy_team_member_id"]), dict(row))
        daily_metrics = [
            dict(row)
            for row in connection.execute(
                """
                SELECT date, today_appts, appt_7_day, cp_ros_mtd
                FROM daily_metrics
                WHERE store_id = ? AND date BETWEEN ? AND ? ORDER BY date
                """,
                (legacy_store_id, period_start.isoformat(), period_end.isoformat()),
            )
        ]
        route_sheet = dict(
            connection.execute(
                """
                SELECT COUNT(*) AS total_rows,
                       SUM(CASE WHEN created_at BETWEEN ? AND ? THEN 1 ELSE 0 END)
                           AS created_in_period
                FROM repair_order WHERE store_id = ?
                """,
                (
                    period_start.isoformat(),
                    f"{period_end.isoformat()} 23:59:59",
                    legacy_store_id,
                ),
            ).fetchone()
        )
        production = dict(
            connection.execute(
                """
                SELECT COUNT(DISTINCT NULLIF(w.ro_number, '')) AS distinct_ros,
                       ROUND(SUM(w.flat_rate_hours), 4) AS produced_frh,
                       COUNT(DISTINCT w.date) AS production_dates
                FROM work_log w
                JOIN team_member tm ON tm.id = w.team_member_id
                JOIN team t ON t.id = tm.team_id
                WHERE t.store_id = ? AND w.date BETWEEN ? AND ?
                """,
                (legacy_store_id, period_start.isoformat(), period_end.isoformat()),
            ).fetchone()
        )

    technician_snapshots = []
    for row in technicians:
        governed = governed_dpo.get(int(row["legacy_team_member_id"]))
        technician_snapshots.append(
            {
                **row,
                "dpo": governed["dpo_value"] if governed else row["dpo"],
                "dpo_mode": (
                    governed["calculation_mode"] if governed else row["dpo_mode"]
                ),
                "effective_period_start": (
                    governed["effective_from"] if governed else period_start.isoformat()
                ),
                "effective_period_end": (
                    governed["effective_to"] if governed else period_end.isoformat()
                ),
                "authority_status": (
                    governed["authority_status"] if governed else "unverified_legacy"
                ),
                "authority_employee_id": (
                    governed["authorized_by_id"] if governed else None
                ),
                "authority_reason": (
                    governed["authorization_reason"] if governed else None
                ),
                "observation_basis": (
                    "effective-dated governed DPO"
                    if governed else "retrospective current-row snapshot"
                ),
            }
        )
    dpo_governance_status = (
        "verified"
        if technician_snapshots
        and all(item["authority_status"] == "verified" for item in technician_snapshots)
        else "unverified_legacy"
    )
    limitations = [
        "Supported demand cannot be reproduced from the available legacy sources.",
        "Appointment counts are two point-in-time snapshots without conversion, mix, or FRH support.",
        "Route-sheet Repair Orders are partial workflow records, not a governed demand ledger.",
        "Produced CDK lines demonstrate realized work, not total supported demand.",
        "Departed-technician deletion prevents complete historical capacity and production attribution.",
    ]
    if dpo_governance_status != "verified":
        limitations.insert(
            4,
            "One or more DPO values lack an effective-dated, verified authority record covering the full period.",
        )
    stable = {
        "enterprise_id": str(scope["enterprise_id"]),
        "managed_store_id": str(scope["managed_store_id"]),
        "department_id": str(scope["department_id"]),
        "legacy_store_id": legacy_store_id,
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "demand_status": "unavailable",
        "supported_demand_frh": None,
        "dpo_governance_status": dpo_governance_status,
        "technicians": technician_snapshots,
        "sources_checked": {
            "daily_metrics": daily_metrics,
            "route_sheet_repair_orders": route_sheet,
            "realized_production": production,
            "production_objective_memo_rows": memo_count,
            "governed_dpo_rows": len(governed_dpo),
        },
        "limitations": limitations,
    }
    encoded = json.dumps(stable, sort_keys=True, separators=(",", ":"))
    return {
        **stable,
        "content_hash": hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
        "observed_at": datetime.now(timezone.utc).isoformat(),
    }


def persist_evidence_pack(
    database_path: str | Path, pack: dict[str, object]
) -> tuple[str, bool]:
    timestamp = datetime.now(timezone.utc).isoformat()
    with closing(sqlite3.connect(database_path)) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        if "true_potential_evidence_packs" not in tables:
            raise ValueError("Run 'flask db upgrade' before applying the evidence pack")
        with connection:
            existing = connection.execute(
                """
                SELECT true_potential_evidence_pack_id
                FROM true_potential_evidence_packs
                WHERE enterprise_id = ? AND content_hash = ?
                """,
                (pack["enterprise_id"], pack["content_hash"]),
            ).fetchone()
            if existing:
                return str(existing[0]), False
            pack_id = uuid4().hex
            snapshot = {
                "technicians": pack["technicians"],
                "supported_demand_frh": pack["supported_demand_frh"],
            }
            connection.execute(
                """
                INSERT INTO true_potential_evidence_packs (
                    true_potential_evidence_pack_id, enterprise_id,
                    managed_store_id, department_id, period_start, period_end,
                    observed_at, demand_status, supported_demand_frh,
                    dpo_governance_status, snapshot_json, source_trace_json,
                    limitations_json, content_hash, created_at, updated_at, version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    pack_id,
                    pack["enterprise_id"],
                    pack["managed_store_id"],
                    pack["department_id"],
                    pack["period_start"],
                    pack["period_end"],
                    pack["observed_at"],
                    pack["demand_status"],
                    pack["supported_demand_frh"],
                    pack["dpo_governance_status"],
                    json.dumps(snapshot, sort_keys=True),
                    json.dumps(pack["sources_checked"], sort_keys=True),
                    json.dumps(pack["limitations"], sort_keys=True),
                    pack["content_hash"],
                    timestamp,
                    timestamp,
                ),
            )
    return pack_id, True

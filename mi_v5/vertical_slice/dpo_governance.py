"""Prospectively authorize effective-dated technician DPO records."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4


def _calculated_dpo(row: sqlite3.Row) -> float:
    productive_days = (
        int(row["hist_days_in_period"] or 0)
        - int(row["hist_training_days"] or 0)
        - int(row["hist_vacation_days"] or 0)
    )
    if productive_days <= 0:
        return 0.0
    lift = float(row["expected_lift_percent"] or 100.0) / 100.0
    return round((float(row["hist_frh_total"] or 0.0) / productive_days) * lift, 4)


def build_current_dpo_plan(
    database_path: str | Path,
    effective_from: date,
    authorized_by_id: str,
    authorization_reason: str,
    legacy_store_id: int = 1,
    authority_status: str = "provisional",
) -> dict[str, object]:
    """Build a read-only prospective plan from active legacy technician rows."""

    reason = authorization_reason.strip()
    if not reason:
        raise ValueError("authorization_reason is required")
    if authority_status not in {"provisional", "verified"}:
        raise ValueError("authority_status must be provisional or verified")
    path = Path(database_path)
    with closing(sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)) as connection:
        connection.row_factory = sqlite3.Row
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        if "technician_dpo_records" not in tables or "retired_at" not in {
            row[1] for row in connection.execute("PRAGMA table_info(team_member)")
        }:
            raise ValueError("Run 'flask db upgrade' before governing DPO")
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
        authority = connection.execute(
            "SELECT employee_id FROM employees WHERE enterprise_id = ? AND employee_id = ?",
            (scope["enterprise_id"], authorized_by_id),
        ).fetchone()
        if authority is None:
            raise ValueError("authorized_by_id must identify an Employee in this Enterprise")
        rows = connection.execute(
            """
            SELECT tm.id, tm.name, tm.tech_number, tm.daily_production_objective,
                   tm.dpo_calculation_mode, tm.hist_frh_total,
                   tm.hist_days_in_period, tm.hist_training_days,
                   tm.hist_vacation_days, tm.expected_lift_percent
            FROM team_member tm
            JOIN team t ON t.id = tm.team_id
            WHERE t.store_id = ? AND tm.retired_at IS NULL
            ORDER BY tm.id
            """,
            (legacy_store_id,),
        ).fetchall()

    technicians = []
    blocking_issues = []
    limitations = []
    for row in rows:
        mode = str(row["dpo_calculation_mode"] or "manual")
        calculated = _calculated_dpo(row)
        member_id = int(row["id"])
        tech_number = str(row["tech_number"] or "").strip()
        dpo_value = float(row["daily_production_objective"] or 0.0)
        if not tech_number:
            blocking_issues.append(
                f"Team member {member_id} ({row['name']}) has no technician number."
            )
        if dpo_value <= 0:
            blocking_issues.append(
                f"Team member {member_id} ({row['name']}) has a non-positive DPO."
            )
        if calculated <= 0:
            limitations.append(
                f"Team member {member_id} ({row['name']}) lacks usable calculation history."
            )
        technicians.append(
            {
                "legacy_team_member_id": member_id,
                "name": row["name"],
                "tech_number": tech_number,
                "dpo_value": dpo_value,
                "calculation_mode": mode,
                "calculated_dpo": calculated,
                "is_override": mode != "calculated",
                "calculation_inputs": {
                    "hist_frh_total": row["hist_frh_total"],
                    "hist_days_in_period": row["hist_days_in_period"],
                    "hist_training_days": row["hist_training_days"],
                    "hist_vacation_days": row["hist_vacation_days"],
                    "expected_lift_percent": row["expected_lift_percent"],
                },
            }
        )
    if authority_status == "verified" and limitations:
        blocking_issues.append(
            "Verified authority requires usable calculation history for every included technician."
        )
    return {
        "enterprise_id": str(scope["enterprise_id"]),
        "managed_store_id": str(scope["managed_store_id"]),
        "department_id": str(scope["department_id"]),
        "legacy_store_id": legacy_store_id,
        "effective_from": effective_from.isoformat(),
        "authorized_by_id": authorized_by_id,
        "authorization_reason": reason,
        "authority_status": authority_status,
        "technicians": technicians,
        "blocking_issues": blocking_issues,
        "limitations": limitations,
    }


def apply_current_dpo_plan(
    database_path: str | Path, plan: dict[str, object]
) -> dict[str, int]:
    """Atomically close prior records and insert the governed prospective set."""

    effective_from = date.fromisoformat(str(plan["effective_from"]))
    if plan.get("blocking_issues"):
        raise ValueError(
            "DPO plan is blocked: " + " ".join(str(item) for item in plan["blocking_issues"])
        )
    close_at = (effective_from - timedelta(days=1)).isoformat()
    inserted = closed = unchanged = 0
    timestamp = datetime.now(timezone.utc).isoformat()
    with closing(sqlite3.connect(database_path)) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        with connection:
            for technician in plan["technicians"]:
                current = connection.execute(
                    """
                    SELECT * FROM technician_dpo_records
                    WHERE enterprise_id = ? AND legacy_team_member_id = ?
                      AND effective_to IS NULL
                    ORDER BY effective_from DESC LIMIT 1
                    """,
                    (plan["enterprise_id"], technician["legacy_team_member_id"]),
                ).fetchone()
                inputs_json = json.dumps(
                    technician["calculation_inputs"], sort_keys=True, separators=(",", ":")
                )
                if current and current["effective_from"] == plan["effective_from"]:
                    same = (
                        float(current["dpo_value"]) == technician["dpo_value"]
                        and current["calculation_mode"] == technician["calculation_mode"]
                        and current["authorized_by_id"] == plan["authorized_by_id"]
                        and current["authorization_reason"] == plan["authorization_reason"]
                        and current["authority_status"] == plan["authority_status"]
                        and current["calculation_inputs_json"] == inputs_json
                    )
                    if not same:
                        raise ValueError(
                            "A different governed record already exists at this effective date "
                            f"for technician {technician['legacy_team_member_id']}"
                        )
                    unchanged += 1
                    continue
                if current:
                    if date.fromisoformat(current["effective_from"]) >= effective_from:
                        raise ValueError("DPO changes must move forward in effective time")
                    connection.execute(
                        """
                        UPDATE technician_dpo_records
                        SET effective_to = ?, updated_at = ?, version = version + 1
                        WHERE technician_dpo_record_id = ?
                        """,
                        (close_at, timestamp, current["technician_dpo_record_id"]),
                    )
                    closed += 1
                connection.execute(
                    """
                    INSERT INTO technician_dpo_records (
                        technician_dpo_record_id, enterprise_id, managed_store_id,
                        department_id, legacy_team_member_id, effective_from,
                        effective_to, dpo_value, calculation_mode, calculated_dpo,
                        is_override, authority_status, authorized_by_id,
                        authorization_reason, calculation_inputs_json,
                        source_reference, created_at, created_by_id, updated_at,
                        updated_by_id, version
                    ) VALUES (?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                              ?, ?, ?, ?, 1)
                    """,
                    (
                        uuid4().hex,
                        plan["enterprise_id"],
                        plan["managed_store_id"],
                        plan["department_id"],
                        technician["legacy_team_member_id"],
                        plan["effective_from"],
                        technician["dpo_value"],
                        technician["calculation_mode"],
                        technician["calculated_dpo"],
                        int(technician["is_override"]),
                        plan["authority_status"],
                        plan["authorized_by_id"],
                        plan["authorization_reason"],
                        inputs_json,
                        "legacy team_member prospective authorization",
                        timestamp,
                        plan["authorized_by_id"],
                        timestamp,
                        plan["authorized_by_id"],
                    ),
                )
                inserted += 1
    return {"inserted": inserted, "closed": closed, "unchanged": unchanged}

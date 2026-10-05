"""Preview prospective Honda Renton DPO governance from PostgreSQL.

Read-only. Current legacy values are candidates, not historical authority.
"""

from __future__ import annotations

import argparse
import json
from contextlib import closing
from datetime import date, datetime
from zoneinfo import ZoneInfo

import psycopg2
from psycopg2.extras import RealDictCursor


def preview(host: str, port: int, dbname: str, user: str,
            expected_database: str, legacy_store_id: int,
            effective_from: date) -> dict:
    today = datetime.now(ZoneInfo("America/Los_Angeles")).date()
    if effective_from < today:
        raise ValueError("DPO effective date must be prospective")
    with closing(psycopg2.connect(
        host=host, port=port, dbname=dbname, user=user
    )) as connection:
        connection.set_session(readonly=True, autocommit=False)
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT current_database() AS name")
            actual = cursor.fetchone()["name"]
            if actual != expected_database:
                raise ValueError(
                    f"Expected database {expected_database!r}; connected to {actual!r}"
                )
            cursor.execute("SELECT version_num FROM alembic_version")
            revision = cursor.fetchone()["version_num"]
            if revision != "e82cd3516d34":
                raise ValueError(f"V5 migration head required; found {revision}")
            cursor.execute(
                """
                SELECT e.enterprise_id, ms.managed_store_id, d.department_id
                FROM enterprises e
                JOIN managed_stores ms ON ms.enterprise_id = e.enterprise_id
                JOIN departments d ON d.enterprise_id = e.enterprise_id
                                  AND d.managed_store_id = ms.managed_store_id
                WHERE ms.external_reference = %s
                  AND d.department_type = 'service'
                  AND ms.status = 'active' AND d.status = 'active'
                """,
                (f"legacy_managed_store:{legacy_store_id}",),
            )
            scope = cursor.fetchone()
            if scope is None:
                raise ValueError("Canonical Honda Renton Service scope is missing")
            cursor.execute(
                """
                SELECT tm.id, tm.tech_number, tm.daily_production_objective,
                       tm.dpo_calculation_mode, tm.hist_frh_total,
                       tm.hist_days_in_period, tm.hist_training_days,
                       tm.hist_vacation_days, tm.expected_lift_percent
                FROM team_member tm
                JOIN team t ON t.id = tm.team_id
                WHERE t.store_id = %s AND tm.retired_at IS NULL
                ORDER BY tm.id
                """,
                (legacy_store_id,),
            )
            rows = cursor.fetchall()
            cursor.execute(
                "SELECT COUNT(*) AS n FROM employees WHERE enterprise_id = %s",
                (scope["enterprise_id"],),
            )
            approver_candidates = cursor.fetchone()["n"]
            cursor.execute(
                """
                SELECT COUNT(*) AS n FROM technician_dpo_records
                WHERE enterprise_id = %s AND managed_store_id = %s
                  AND department_id = %s
                """,
                (scope["enterprise_id"], scope["managed_store_id"],
                 scope["department_id"]),
            )
            existing_records = cursor.fetchone()["n"]

    technicians = []
    issues = []
    for row in rows:
        member_id = row["id"]
        productive_days = (
            int(row["hist_days_in_period"] or 0)
            - int(row["hist_training_days"] or 0)
            - int(row["hist_vacation_days"] or 0)
        )
        calculated = (
            round(
                float(row["hist_frh_total"] or 0) / productive_days
                * float(row["expected_lift_percent"] or 100) / 100,
                4,
            )
            if productive_days > 0 else 0.0
        )
        current = float(row["daily_production_objective"] or 0)
        if not (row["tech_number"] or "").strip():
            issues.append(f"Technician {member_id} lacks a technician number")
        if current <= 0:
            issues.append(f"Technician {member_id} has non-positive DPO")
        if calculated <= 0:
            issues.append(f"Technician {member_id} lacks usable calculation history")
        technicians.append({
            "legacy_team_member_id": member_id,
            "tech_number": row["tech_number"],
            "current_manual_dpo": current,
            "calculated_comparison": calculated,
            "calculation_mode": row["dpo_calculation_mode"],
            "requires_override_review": row["dpo_calculation_mode"] != "calculated",
        })
    if not rows:
        issues.append("No active technicians found")
    if not approver_candidates:
        issues.append("No canonical Employee exists to approve DPO authority")
    return {
        "mode": "preview_only",
        "database": actual,
        "legacy_store_id": legacy_store_id,
        "enterprise_id": str(scope["enterprise_id"]),
        "managed_store_id": str(scope["managed_store_id"]),
        "department_id": str(scope["department_id"]),
        "effective_from": effective_from.isoformat(),
        "technician_count": len(technicians),
        "existing_governed_records": existing_records,
        "canonical_employee_count": approver_candidates,
        "blocking_issues": issues,
        "technicians": technicians,
        "authority_created": False,
        "historical_dpo_verified": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", required=True, type=int)
    parser.add_argument("--dbname", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--expected-database", required=True)
    parser.add_argument("--legacy-store-id", required=True, type=int)
    parser.add_argument("--effective-from", required=True, type=date.fromisoformat)
    args = parser.parse_args()
    print(json.dumps(preview(**vars(args)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

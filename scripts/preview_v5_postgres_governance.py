"""Read-only canonical authority and human DPO review preview for isolated V5.

There is no apply mode. Never creates an Employee, Assignment, grant or DPO.
"""

from __future__ import annotations

import argparse
import json
import sys
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mi_v5.schema_versions import ASSIGNMENT_REVISION, ISOLATED_V5_DATABASE
from mi_v5.vertical_slice.dpo_approval import build_proposal


def read_snapshot(host, port, dbname, user, *, connection_factory=None,
                  cursor_factory=None):
    if dbname != ISOLATED_V5_DATABASE:
        raise ValueError("Only the isolated dpo_v5_beta database is supported")
    if connection_factory is None:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        connection_factory = psycopg2.connect
        cursor_factory = RealDictCursor
    with closing(connection_factory(
        host=host, port=port, dbname=dbname, user=user
    )) as connection:
        connection.set_session(
            readonly=True, autocommit=False, isolation_level="REPEATABLE READ"
        )
        with connection.cursor(cursor_factory=cursor_factory) as cursor:
            cursor.execute("SELECT current_database() AS name")
            actual = cursor.fetchone()["name"]
            if actual != ISOLATED_V5_DATABASE:
                raise ValueError("Connected database differs from the isolated target")
            cursor.execute("SELECT version_num FROM alembic_version")
            revision = cursor.fetchone()["version_num"]
            if revision != ASSIGNMENT_REVISION:
                raise ValueError("Canonical Assignment migration is required")
            cursor.execute("""
                SELECT e.enterprise_id, e.name AS enterprise_name,
                       e.status AS enterprise_status,
                       e.retired_at AS enterprise_retired_at,
                       ms.managed_store_id, ms.name AS store_name,
                       ms.store_code, ms.external_reference,
                       ms.status AS store_status, ms.retired_at AS store_retired_at,
                       d.department_id, d.code AS department_code,
                       d.department_type, d.status AS department_status,
                       d.retired_at AS department_retired_at,
                       d.effective_from AS department_effective_from,
                       d.effective_to AS department_effective_to
                FROM enterprises e
                JOIN managed_stores ms ON ms.enterprise_id = e.enterprise_id
                JOIN departments d ON d.enterprise_id = e.enterprise_id
                                  AND d.managed_store_id = ms.managed_store_id
                WHERE ms.external_reference = %s
                  AND e.name = %s AND ms.store_code = %s AND ms.name = %s
                  AND d.code = %s AND d.department_type = 'service'
            """, ("legacy_managed_store:2", "AutoNation", "HONDA_RENTON",
                  "Honda Renton", "SERVICE"))
            scopes = cursor.fetchall()
            if len(scopes) != 1:
                raise ValueError("Honda Renton Service scope is missing or ambiguous")
            scope = dict(scopes[0])
            cursor.execute("SELECT name FROM managed_store WHERE id = %s", (2,))
            legacy = cursor.fetchone()
            if legacy is None or legacy["name"] != "Honda Renton":
                raise ValueError("Legacy store 2 is not Honda Renton")
            enterprise = scope["enterprise_id"]
            snapshot = {"database": actual, "migration": revision, "scope": scope}
            queries = {
                "employees": """SELECT employee_id, enterprise_id, status, retired_at
                                FROM employees WHERE enterprise_id = %s""",
                "roles": """SELECT role_id, enterprise_id, status, retired_at,
                                   effective_from, effective_to
                            FROM roles WHERE enterprise_id = %s""",
                "assignments": "SELECT * FROM assignments WHERE enterprise_id = %s",
                "capabilities": """SELECT capability_id, enterprise_id, "key",
                                          status, retired_at, effective_from, effective_to
                                   FROM capabilities WHERE enterprise_id = %s""",
                "role_grants": """SELECT * FROM role_capability_assignments
                                 WHERE enterprise_id = %s""",
                "existing_dpos": """SELECT * FROM technician_dpo_records
                                   WHERE enterprise_id = %s""",
            }
            for key, statement in queries.items():
                cursor.execute(statement, (enterprise,))
                snapshot[key] = [dict(row) for row in cursor.fetchall()]
            cursor.execute("""
                SELECT tm.id, tm.tech_number, tm.daily_production_objective,
                       tm.dpo_calculation_mode, tm.hist_frh_total,
                       tm.hist_days_in_period, tm.hist_training_days,
                       tm.hist_vacation_days, tm.expected_lift_percent
                FROM team_member tm JOIN team t ON t.id = tm.team_id
                WHERE t.store_id = %s AND tm.retired_at IS NULL ORDER BY tm.id
            """, (2,))
            snapshot["technicians"] = [dict(row) for row in cursor.fetchall()]
    return snapshot


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", required=True, type=int)
    parser.add_argument("--dbname", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument(
        "--review", type=Path,
        help="Explicit human review JSON. Omit to show blocked candidate record shapes.",
    )
    args = parser.parse_args()
    review = json.loads(args.review.read_text(encoding="utf-8")) if args.review else {}
    snapshot = read_snapshot(args.host, args.port, args.dbname, args.user)
    proposal = build_proposal(snapshot, review, now=datetime.now(timezone.utc))
    print(json.dumps(proposal, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

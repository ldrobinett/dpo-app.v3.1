"""Read a scoped, aggregate ProdTracker evidence snapshot from PostgreSQL.

This is a legacy source bridge. It does not authorize DPO, establish supported
demand, or create a canonical V5 StorePeriodEvidence record.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import date, datetime, timezone

import psycopg2
from psycopg2.extras import RealDictCursor


QUERY_VERSION = "legacy-postgres-evidence-v1"


def extract_period(database_url: str, store_id: int, start: date, end: date) -> dict:
    if end < start:
        raise ValueError("period_end must be on or after period_start")
    if store_id <= 0:
        raise ValueError("store_id must be positive")

    with psycopg2.connect(database_url) as connection:
        connection.set_session(readonly=True)
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT id, name FROM managed_store WHERE id = %s",
                (store_id,),
            )
            store = cursor.fetchone()
            if store is None:
                raise ValueError(f"Managed store {store_id} does not exist")

            cursor.execute(
                """
                SELECT COUNT(*) AS scheduled_rows,
                       COUNT(DISTINCT se.date) AS scheduled_dates,
                       COUNT(DISTINCT se.team_member_id) AS scheduled_technicians,
                       COALESCE(SUM(tm.daily_production_objective), 0)
                           AS legacy_dpo_capacity_frh
                FROM schedule_entry se
                JOIN team_member tm ON tm.id = se.team_member_id
                JOIN team t ON t.id = tm.team_id
                WHERE t.store_id = %s AND se.schedule_type = 'WORK'
                  AND se.date BETWEEN %s AND %s
                """,
                (store_id, start, end),
            )
            schedule = dict(cursor.fetchone())

            cursor.execute(
                """
                SELECT COUNT(*) AS work_log_rows,
                       COUNT(DISTINCT w.date) AS production_dates,
                       COUNT(DISTINCT w.team_member_id) AS producing_technicians,
                       COUNT(DISTINCT NULLIF(w.ro_number, '')) AS distinct_ro_ids,
                       COALESCE(SUM(w.flat_rate_hours), 0) AS realized_frh,
                       COUNT(*) FILTER (WHERE w.flat_rate_hours > 0) AS positive_rows,
                       COUNT(*) FILTER (WHERE w.flat_rate_hours = 0) AS zero_rows,
                       COUNT(*) FILTER (WHERE w.flat_rate_hours < 0) AS negative_rows,
                       MAX(w.date) AS latest_production_date
                FROM work_log w
                JOIN team_member tm ON tm.id = w.team_member_id
                JOIN team t ON t.id = tm.team_id
                WHERE t.store_id = %s AND w.date BETWEEN %s AND %s
                """,
                (store_id, start, end),
            )
            production = dict(cursor.fetchone())

            cursor.execute(
                """
                SELECT DISTINCT se.date
                FROM schedule_entry se
                JOIN team_member tm ON tm.id = se.team_member_id
                JOIN team t ON t.id = tm.team_id
                WHERE t.store_id = %s AND se.schedule_type = 'WORK'
                  AND se.date BETWEEN %s AND %s
                  AND NOT EXISTS (
                      SELECT 1 FROM work_log w
                      JOIN team_member wt ON wt.id = w.team_member_id
                      JOIN team wteam ON wteam.id = wt.team_id
                      WHERE wteam.store_id = t.store_id AND w.date = se.date
                  )
                ORDER BY se.date
                """,
                (store_id, start, end),
            )
            continuity_gaps = [row["date"].isoformat() for row in cursor.fetchall()]

            cursor.execute(
                """
                SELECT tm.dpo_calculation_mode, COUNT(*) AS technician_count
                FROM team_member tm JOIN team t ON t.id = tm.team_id
                WHERE t.store_id = %s
                GROUP BY tm.dpo_calculation_mode
                """,
                (store_id,),
            )
            dpo_modes = {
                str(row["dpo_calculation_mode"] or "unknown"): row["technician_count"]
                for row in cursor.fetchall()
            }

            cursor.execute(
                """
                SELECT COUNT(*) AS snapshot_count, MAX(date) AS latest_snapshot_date
                FROM daily_metrics WHERE store_id = %s
                  AND date BETWEEN %s AND %s
                """,
                (store_id, start, end),
            )
            daily = dict(cursor.fetchone())

            cursor.execute(
                """
                SELECT COUNT(*) AS input_rows,
                       COUNT(*) FILTER (
                           WHERE fi.cp_effective_labor_rate IS NOT NULL
                             AND fi.cp_parts_to_labor_ratio IS NOT NULL
                             AND fi.cp_labor_margin IS NOT NULL
                             AND fi.cp_parts_margin IS NOT NULL
                       ) AS complete_cp_economic_rows
                FROM financial_inputs fi
                JOIN "user" u ON u.id = fi.user_id
                WHERE u.store_id = %s
                """,
                (store_id,),
            )
            economics = dict(cursor.fetchone())

            cursor.execute(
                "SELECT to_regclass('public.technician_dpo_records') IS NOT NULL AS present"
            )
            governed_dpo_table_present = bool(cursor.fetchone()["present"])

    def encode(value):
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        if hasattr(value, "as_tuple"):  # Decimal
            return float(value)
        if isinstance(value, dict):
            return {key: encode(item) for key, item in value.items()}
        return value

    return encode({
        "query_version": QUERY_VERSION,
        "extracted_at": datetime.now(timezone.utc),
        "legacy_store_id": store_id,
        "store_name": store["name"],
        "period_start": start,
        "period_end": end,
        "schedule": schedule,
        "production": production,
        "continuity_gap_dates": continuity_gaps,
        "dpo_modes": dpo_modes,
        "governed_dpo_table_present": governed_dpo_table_present,
        "daily_metrics": daily,
        "economics": economics,
        "supported_demand_frh": None,
        "validation_status": "legacy_evidence_only",
        "limitations": [
            "Current team_member DPO values are a retrospective snapshot, not verified effective-dated authority.",
            "Supported demand is unavailable from this legacy extraction.",
            "RO identifiers and realized production do not establish total demand.",
            "A complete CP economic row is an input check, not transaction-level realized economics.",
        ],
    })


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store-id", type=int, required=True)
    parser.add_argument("--period-start", type=date.fromisoformat, required=True)
    parser.add_argument("--period-end", type=date.fromisoformat, required=True)
    args = parser.parse_args()
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        parser.error("DATABASE_URL is required; do not pass credentials on the command line")
    result = extract_period(
        database_url, args.store_id, args.period_start, args.period_end
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

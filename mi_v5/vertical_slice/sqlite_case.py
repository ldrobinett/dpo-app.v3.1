"""Read one governed service case from the existing ProdTracker SQLite store."""

from __future__ import annotations

import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path

from .contracts import (
    EconomicInputs,
    SourceReference,
    StorePeriodEvidence,
    TechnicianPotentialInput,
)

QUERY_VERSION = "prodtracker-sqlite-case-v1"


def _parse_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def _first_value(row: sqlite3.Row | None, *names: str) -> float | None:
    if row is None:
        return None
    for name in names:
        value = row[name]
        if value is not None:
            return float(value)
    return None


def load_store_period(
    database_path: str | Path,
    period_start: date,
    period_end: date,
    legacy_store_id: int = 1,
) -> StorePeriodEvidence:
    """Load a read-only store-period snapshot with explicit source lineage."""

    if period_end < period_start:
        raise ValueError("period_end must be on or after period_start")

    path = Path(database_path)
    if not path.exists():
        raise FileNotFoundError(path)

    connection = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        scope = connection.execute(
            """
            SELECT e.enterprise_id, ms.managed_store_id, d.department_id
            FROM enterprises e
            JOIN managed_stores ms ON ms.enterprise_id = e.enterprise_id
            JOIN departments d
              ON d.enterprise_id = e.enterprise_id
             AND d.managed_store_id = ms.managed_store_id
            WHERE d.department_type = 'service'
            ORDER BY d.effective_from
            LIMIT 1
            """
        ).fetchone()
        if scope is None:
            raise ValueError(
                "A V5 Enterprise, Managed Store, and Service Department are required"
            )

        team_rows = connection.execute(
            """
            SELECT tm.id, tm.daily_production_objective,
                   tm.dpo_calculation_mode, tm.hist_frh_total,
                   tm.hist_days_in_period, tm.expected_lift_percent
            FROM team_member tm
            JOIN team t ON t.id = tm.team_id
            WHERE t.store_id = ?
            ORDER BY tm.id
            """,
            (legacy_store_id,),
        ).fetchall()

        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        governed_dpo: dict[int, sqlite3.Row] = {}
        if "technician_dpo_records" in tables:
            for row in connection.execute(
                """
                SELECT legacy_team_member_id, dpo_value, calculation_mode,
                       authority_status, effective_from, effective_to
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
                governed_dpo.setdefault(int(row["legacy_team_member_id"]), row)

        schedule_rows = connection.execute(
            """
            SELECT se.team_member_id, se.date
            FROM schedule_entry se
            JOIN team_member tm ON tm.id = se.team_member_id
            JOIN team t ON t.id = tm.team_id
            WHERE t.store_id = ?
              AND se.schedule_type = 'WORK'
              AND se.date BETWEEN ? AND ?
            ORDER BY se.team_member_id, se.date
            """,
            (legacy_store_id, period_start.isoformat(), period_end.isoformat()),
        ).fetchall()
        schedules: dict[int, list[date]] = {}
        for row in schedule_rows:
            schedules.setdefault(int(row["team_member_id"]), []).append(
                date.fromisoformat(row["date"])
            )

        technicians = tuple(
            TechnicianPotentialInput(
                technician_id=int(row["id"]),
                dpo=float(
                    governed_dpo[int(row["id"])]["dpo_value"]
                    if int(row["id"]) in governed_dpo
                    else row["daily_production_objective"] or 0.0
                ),
                dpo_mode=str(
                    governed_dpo[int(row["id"])]["calculation_mode"]
                    if int(row["id"]) in governed_dpo
                    else row["dpo_calculation_mode"] or "unknown"
                ),
                scheduled_dates=tuple(schedules.get(int(row["id"]), ())),
                history_frh=(
                    float(row["hist_frh_total"])
                    if row["hist_frh_total"] is not None
                    else None
                ),
                history_days=(
                    int(row["hist_days_in_period"])
                    if row["hist_days_in_period"] is not None
                    else None
                ),
                expected_lift_percent=(
                    float(row["expected_lift_percent"])
                    if row["expected_lift_percent"] is not None
                    else None
                ),
                governance_status=(
                    str(governed_dpo[int(row["id"])]["authority_status"])
                    if int(row["id"]) in governed_dpo
                    else "unverified_legacy"
                ),
            )
            for row in team_rows
        )

        production = connection.execute(
            """
            SELECT COALESCE(SUM(w.flat_rate_hours), 0) AS actual_frh,
                   COUNT(DISTINCT NULLIF(w.ro_number, '')) AS ro_count,
                   MAX(w.date) AS latest_date
            FROM work_log w
            JOIN team_member tm ON tm.id = w.team_member_id
            JOIN team t ON t.id = tm.team_id
            WHERE t.store_id = ? AND w.date BETWEEN ? AND ?
            """,
            (legacy_store_id, period_start.isoformat(), period_end.isoformat()),
        ).fetchone()
        production_dates = tuple(
            date.fromisoformat(row["date"])
            for row in connection.execute(
                """
                SELECT DISTINCT w.date
                FROM work_log w
                JOIN team_member tm ON tm.id = w.team_member_id
                JOIN team t ON t.id = tm.team_id
                WHERE t.store_id = ? AND w.date BETWEEN ? AND ?
                ORDER BY w.date
                """,
                (legacy_store_id, period_start.isoformat(), period_end.isoformat()),
            )
        )

        daily = connection.execute(
            """
            SELECT date, total_gross
            FROM daily_metrics
            WHERE store_id = ? AND date BETWEEN ? AND ?
            ORDER BY date DESC
            LIMIT 1
            """,
            (legacy_store_id, period_start.isoformat(), period_end.isoformat()),
        ).fetchone()

        financial = connection.execute(
            """
            SELECT fi.*
            FROM financial_inputs fi
            JOIN user u ON u.id = fi.user_id
            WHERE u.store_id = ?
            ORDER BY fi.id
            LIMIT 1
            """,
            (legacy_store_id,),
        ).fetchone()
        economics = EconomicInputs(
            effective_labor_rate=_first_value(
                financial, "cp_effective_labor_rate", "effective_labor_rate"
            ),
            parts_to_labor_ratio=_first_value(
                financial, "cp_parts_to_labor_ratio", "parts_to_labor_ratio"
            ),
            labor_margin=_first_value(
                financial, "cp_labor_margin", "labor_margin"
            ),
            parts_margin=_first_value(
                financial, "cp_parts_margin", "parts_margin"
            ),
            source_scope=(
                "customer_pay"
                if financial and financial["cp_effective_labor_rate"] is not None
                else "general_service_fallback"
            ),
        )

        owner = connection.execute(
            """
            SELECT ea.employee_id, ea.position_id
            FROM employee_assignments ea
            JOIN positions p
              ON p.enterprise_id = ea.enterprise_id
             AND p.position_id = ea.position_id
            WHERE p.department_id = ?
              AND p.is_managerial = 1
              AND ea.status = 'active'
              AND ea.effective_to IS NULL
            ORDER BY ea.is_primary DESC, ea.effective_from
            LIMIT 1
            """,
            (scope["department_id"],),
        ).fetchone()

        scheduled_dates = tuple(
            sorted({item for dates in schedules.values() for item in dates})
        )
        latest_production = _parse_date(
            production["latest_date"] if production else None
        )
        daily_date = _parse_date(daily["date"] if daily else None)
        work_log_count = connection.execute(
            """
            SELECT COUNT(*) FROM work_log w
            JOIN team_member tm ON tm.id = w.team_member_id
            JOIN team t ON t.id = tm.team_id
            WHERE t.store_id = ? AND w.date BETWEEN ? AND ?
            """,
            (legacy_store_id, period_start.isoformat(), period_end.isoformat()),
        ).fetchone()[0]

        return StorePeriodEvidence(
            enterprise_id=str(scope["enterprise_id"]),
            managed_store_id=str(scope["managed_store_id"]),
            department_id=str(scope["department_id"]),
            legacy_store_id=legacy_store_id,
            period_start=period_start,
            period_end=period_end,
            extracted_at=datetime.now(timezone.utc),
            technicians=technicians,
            production_dates=production_dates,
            scheduled_operating_dates=scheduled_dates,
            actual_frh=float(production["actual_frh"] or 0.0),
            repair_order_count=int(production["ro_count"] or 0),
            actual_mtd_gross=(float(daily["total_gross"]) if daily else None),
            actual_mtd_gross_date=daily_date,
            supported_demand_frh=None,
            economics=economics,
            accountable_owner_id=(str(owner["employee_id"]) if owner else None),
            accountable_position_id=(str(owner["position_id"]) if owner else None),
            sources=(
                SourceReference(
                    source="work_log",
                    query_version=QUERY_VERSION,
                    record_count=work_log_count,
                    latest_observed_date=latest_production,
                ),
                SourceReference(
                    source="schedule_entry",
                    query_version=QUERY_VERSION,
                    record_count=len(schedule_rows),
                    latest_observed_date=max(scheduled_dates, default=None),
                ),
                SourceReference(
                    source=(
                        "technician_dpo_records"
                        if governed_dpo else "team_member.dpo"
                    ),
                    query_version=QUERY_VERSION,
                    record_count=(len(governed_dpo) if governed_dpo else len(team_rows)),
                    limitations=(
                        ()
                        if len(governed_dpo) == len(team_rows)
                        else (
                            "One or more technician DPO values lack a verified record covering the full period.",
                        )
                    ),
                ),
                SourceReference(
                    source="daily_metrics",
                    query_version=QUERY_VERSION,
                    record_count=(1 if daily else 0),
                    latest_observed_date=daily_date,
                ),
                SourceReference(
                    source="financial_inputs",
                    query_version=QUERY_VERSION,
                    record_count=(1 if financial else 0),
                    limitations=(
                        "General service economics are used when CP-specific fields are absent.",
                    )
                    if economics.source_scope != "customer_pay"
                    else (),
                ),
            ),
        )
    finally:
        connection.close()

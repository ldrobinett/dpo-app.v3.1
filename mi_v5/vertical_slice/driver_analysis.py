"""Reproducible period-driver decomposition without unsupported causation."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path


def analyze_period_drivers(
    database_path: str | Path,
    period_start: date,
    period_end: date,
    legacy_store_id: int = 1,
) -> dict[str, object]:
    if period_end < period_start:
        raise ValueError("period_end must be on or after period_start")
    path = Path(database_path)
    with closing(sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)) as connection:
        connection.row_factory = sqlite3.Row
        production = dict(
            connection.execute(
                """
                SELECT COUNT(*) AS line_count,
                       COUNT(DISTINCT NULLIF(trim(w.ro_number), '')) AS ro_count,
                       COUNT(DISTINCT w.date) AS production_dates,
                       ROUND(COALESCE(SUM(w.flat_rate_hours), 0), 4) AS actual_frh
                FROM work_log w
                JOIN team_member tm ON tm.id = w.team_member_id
                JOIN team t ON t.id = tm.team_id
                WHERE t.store_id = ? AND w.date BETWEEN ? AND ?
                """,
                (legacy_store_id, period_start.isoformat(), period_end.isoformat()),
            ).fetchone()
        )
        ro_distribution = dict(
            connection.execute(
                """
                WITH ro_totals AS (
                    SELECT trim(w.ro_number) AS ro_number,
                           SUM(w.flat_rate_hours) AS frh
                    FROM work_log w
                    JOIN team_member tm ON tm.id = w.team_member_id
                    JOIN team t ON t.id = tm.team_id
                    WHERE t.store_id = ? AND w.date BETWEEN ? AND ?
                      AND NULLIF(trim(w.ro_number), '') IS NOT NULL
                    GROUP BY trim(w.ro_number)
                )
                SELECT ROUND(AVG(frh), 4) AS average_frh_per_ro,
                       ROUND(MIN(frh), 4) AS minimum_frh_per_ro,
                       ROUND(MAX(frh), 4) AS maximum_frh_per_ro,
                       SUM(CASE WHEN frh < 0 THEN 1 ELSE 0 END) AS negative_frh_ros,
                       SUM(CASE WHEN frh = 0 THEN 1 ELSE 0 END) AS zero_frh_ros,
                       SUM(CASE WHEN frh > 0 THEN 1 ELSE 0 END) AS positive_frh_ros
                FROM ro_totals
                """,
                (legacy_store_id, period_start.isoformat(), period_end.isoformat()),
            ).fetchone()
        )
        technicians = [
            dict(row)
            for row in connection.execute(
                """
                SELECT tm.id AS legacy_team_member_id, tm.tech_number,
                       ROUND(SUM(w.flat_rate_hours), 4) AS actual_frh,
                       COUNT(DISTINCT NULLIF(trim(w.ro_number), '')) AS ro_count
                FROM work_log w
                JOIN team_member tm ON tm.id = w.team_member_id
                JOIN team t ON t.id = tm.team_id
                WHERE t.store_id = ? AND w.date BETWEEN ? AND ?
                GROUP BY tm.id, tm.tech_number
                ORDER BY actual_frh DESC, tm.id
                """,
                (legacy_store_id, period_start.isoformat(), period_end.isoformat()),
            )
        ]
        latest_metrics_row = connection.execute(
            """
            SELECT date, total_gross, labor_gross, parts_gross, sublet_gross,
                   cp_ros_mtd
            FROM daily_metrics
            WHERE store_id = ? AND date BETWEEN ? AND ?
            ORDER BY date DESC LIMIT 1
            """,
            (legacy_store_id, period_start.isoformat(), period_end.isoformat()),
        ).fetchone()
        financial_row = connection.execute(
            """
            SELECT fi.cp_effective_labor_rate, fi.effective_labor_rate,
                   fi.cp_parts_to_labor_ratio, fi.parts_to_labor_ratio,
                   fi.cp_labor_margin, fi.labor_margin,
                   fi.cp_parts_margin, fi.parts_margin
            FROM financial_inputs fi
            JOIN user u ON u.id = fi.user_id
            WHERE u.store_id = ? ORDER BY fi.id LIMIT 1
            """,
            (legacy_store_id,),
        ).fetchone()

    actual_frh = float(production["actual_frh"] or 0.0)
    ro_count = int(production["ro_count"] or 0)
    production_dates = int(production["production_dates"] or 0)
    top_five_frh = sum(float(row["actual_frh"] or 0.0) for row in technicians[:5])
    metrics = dict(latest_metrics_row) if latest_metrics_row else None

    def first(row: sqlite3.Row | None, primary: str, fallback: str) -> float | None:
        if row is None:
            return None
        value = row[primary] if row[primary] is not None else row[fallback]
        return float(value) if value is not None else None

    elr = first(financial_row, "cp_effective_labor_rate", "effective_labor_rate")
    parts_ratio = first(financial_row, "cp_parts_to_labor_ratio", "parts_to_labor_ratio")
    labor_margin = first(financial_row, "cp_labor_margin", "labor_margin")
    parts_margin = first(financial_row, "cp_parts_margin", "parts_margin")
    configured_gp_per_frh = None
    if None not in (elr, parts_ratio, labor_margin, parts_margin):
        configured_gp_per_frh = round(
            elr * (labor_margin / 100.0)
            + (elr * parts_ratio) * (parts_margin / 100.0),
            4,
        )

    observed_total_gross = float(metrics["total_gross"] or 0.0) if metrics else None
    observed_cp_ros = int(metrics["cp_ros_mtd"] or 0) if metrics else None
    return {
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "production": {
            **production,
            **ro_distribution,
            "frh_per_ro": round(actual_frh / ro_count, 4) if ro_count else None,
            "frh_per_production_date": (
                round(actual_frh / production_dates, 4) if production_dates else None
            ),
        },
        "technician_distribution": {
            "producing_technician_count": len(technicians),
            "top_five_frh_share": (
                round(top_five_frh / actual_frh, 4) if actual_frh else None
            ),
            "technicians": technicians,
        },
        "latest_period_metrics": metrics,
        "observed_economics": {
            "gross_per_cp_ro": (
                round(observed_total_gross / observed_cp_ros, 4)
                if observed_total_gross is not None and observed_cp_ros
                else None
            ),
            "gross_per_actual_frh": (
                round(observed_total_gross / actual_frh, 4)
                if observed_total_gross is not None and actual_frh
                else None
            ),
        },
        "configured_economic_assumptions": {
            "effective_labor_rate": elr,
            "parts_to_labor_ratio": parts_ratio,
            "labor_margin": labor_margin,
            "parts_margin": parts_margin,
            "margin_unit": "percent",
            "estimated_gp_per_frh": configured_gp_per_frh,
        },
        "causal_boundary": {
            "supported_demand": "unavailable",
            "volume_driver": "described_not_benchmarked",
            "hours_per_ro_driver": "described_not_benchmarked",
            "rate_and_margin_driver": (
                "partial_snapshot_and_configured_assumptions"
                if metrics and configured_gp_per_frh is not None
                else "unavailable"
            ),
            "process_cause": "unresolved",
            "correction_allowed": False,
        },
        "limitations": [
            "RO volume and FRH per RO are observed, but no governed target or comparable baseline is present.",
            "The latest daily metrics row is a point-in-time MTD snapshot, not transaction-level economic lineage.",
            "Configured ELR and margin values are assumptions unless independently reconciled to the period.",
            "Supported demand is unavailable, so unused capacity cannot be classified as lost production.",
        ],
    }

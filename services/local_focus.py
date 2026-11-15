"""Store manager-entered rehearsal decisions alongside an isolated SQLite pilot."""

import hashlib
import json
import sqlite3
from contextlib import closing, contextmanager
from datetime import date
from pathlib import Path


def snapshot_key(snapshot):
    payload = json.dumps(snapshot, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@contextmanager
def focus_records(database):
    path = Path(database).with_suffix(".focus.sqlite")
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS focus_decisions (
                id INTEGER PRIMARY KEY, store_id INTEGER NOT NULL,
                snapshot_key TEXT NOT NULL, snapshot TEXT NOT NULL,
                entered_by TEXT NOT NULL, entered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                disposition TEXT NOT NULL, rationale TEXT NOT NULL,
                owner TEXT, due_date TEXT, action TEXT, expected_result TEXT,
                UNIQUE (store_id, snapshot_key)
            );
            CREATE TABLE IF NOT EXISTS focus_reviews (
                id INTEGER PRIMARY KEY, decision_id INTEGER NOT NULL REFERENCES focus_decisions(id),
                entered_by TEXT NOT NULL, entered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                completed TEXT NOT NULL, outcome TEXT NOT NULL, observed TEXT NOT NULL,
                evidence_reference TEXT NOT NULL, observed_on TEXT NOT NULL
            );
        """)
        yield connection


def list_decisions(connection, store_id):
    return connection.execute("""
        SELECT d.id, d.snapshot_key, d.snapshot, d.disposition, d.rationale, d.action, d.owner,
               d.due_date, d.entered_by, d.expected_result,
               r.completed AS latest_completion, r.outcome AS latest_outcome, r.observed_on,
               r.observed, r.evidence_reference
        FROM focus_decisions d
        LEFT JOIN focus_reviews r ON r.id = (
            SELECT MAX(id) FROM focus_reviews WHERE decision_id = d.id
        )
        WHERE d.store_id = ? ORDER BY d.id DESC
    """, (store_id,)).fetchall()


def action_status(due_date, completion, outcome, today):
    labels = {"worked": "Worked", "partial": "Partly worked", "missed": "Missed the target"}
    if not due_date:
        return "decision", "No action assigned", "—"
    if completion == "done":
        return ("reviewed", "Completed", labels[outcome]) if outcome in labels else (
            "check", "Completed", "Check the result"
        )
    deadline = date.fromisoformat(due_date)
    if deadline < today:
        return "overdue", "Overdue", "Awaiting completion"
    if deadline == today:
        return "due", "Due today", "Awaiting completion"
    return "open", "Open", "Awaiting completion"


def action_rows(connection, store_id, today):
    rows = []
    for record in list_decisions(connection, store_id):
        row = dict(record)
        snapshot = json.loads(row.pop("snapshot"))
        row["calculator"] = snapshot.get("calculator")
        row["subject"] = snapshot.get("tsi_development", {}).get("job") or snapshot.get("sci_coverage", {}).get("subject")
        row["stage"], row["work_status"], row["result_status"] = action_status(
            row["due_date"], row["latest_completion"], row["latest_outcome"], today,
        )
        rows.append(row)
    priority = {stage: i for i, stage in enumerate(("overdue", "due", "check", "open", "reviewed", "decision"))}
    return sorted(rows, key=lambda row: (priority[row["stage"]], row["due_date"] or "", -row["id"]))

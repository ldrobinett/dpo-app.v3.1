"""Evidence-backed technician development records in the isolated pilot."""

import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path

from models import Team, TeamMember


def active_technicians(store_id, today):
    members = TeamMember.query.join(Team).filter(Team.store_id == store_id).order_by(TeamMember.name)
    return {member.id: member.name for member in members
            if not member.retired_at or member.retired_at.date() > today}


@contextmanager
def development_records(database):
    with closing(sqlite3.connect(Path(database).with_suffix(".tsi.sqlite"))) as connection, connection:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS critical_jobs (
                id INTEGER PRIMARY KEY, store_id INTEGER NOT NULL,
                name TEXT NOT NULL COLLATE NOCASE, coverage_target INTEGER NOT NULL,
                UNIQUE (store_id, name)
            );
            CREATE TABLE IF NOT EXISTS skill_checks (
                id INTEGER PRIMARY KEY,
                job_id INTEGER NOT NULL REFERENCES critical_jobs(id),
                technician_id INTEGER NOT NULL, status TEXT NOT NULL,
                observed_on TEXT NOT NULL, evidence TEXT NOT NULL, entered_by TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS critical_responsibilities (
                id INTEGER PRIMARY KEY, store_id INTEGER NOT NULL,
                name TEXT NOT NULL COLLATE NOCASE, primary_person TEXT NOT NULL,
                UNIQUE (store_id, name)
            );
            CREATE TABLE IF NOT EXISTS backup_checks (
                id INTEGER PRIMARY KEY,
                responsibility_id INTEGER NOT NULL REFERENCES critical_responsibilities(id),
                person TEXT NOT NULL, status TEXT NOT NULL, observed_on TEXT NOT NULL,
                evidence TEXT NOT NULL, entered_by TEXT NOT NULL
            );
        """)
        yield connection


def job_depth(connection, store_id, roster):
    jobs = {row["id"]: dict(row, learning=[], independent=[], needs_training=[], verified=0) for row in connection.execute(
        "SELECT * FROM critical_jobs WHERE store_id = ? ORDER BY name", (store_id,)
    )}
    checks = connection.execute("""
        SELECT s.* FROM skill_checks s JOIN critical_jobs j ON j.id = s.job_id
        WHERE j.store_id = ? ORDER BY s.observed_on DESC, s.id DESC
    """, (store_id,))
    seen = set()
    for check in checks:
        key = check["job_id"], check["technician_id"]
        if key in seen or check["technician_id"] not in roster:
            continue
        seen.add(key)
        job = jobs[check["job_id"]]
        job["verified"] += 1
        job[check["status"]].append(dict(check, technician=roster[check["technician_id"]]))
    for job in jobs.values():
        job["unknown"] = len(roster) - job["verified"]
        job["gap"] = max(0, job["coverage_target"] - len(job["independent"]))
        for status in ("learning", "independent", "needs_training"):
            job[status].sort(key=lambda row: row["technician"].casefold())
    return jobs


def responsibility_coverage(connection, store_id):
    responsibilities = {row["id"]: dict(row, backups=[], unconfirmed=[]) for row in connection.execute(
        "SELECT * FROM critical_responsibilities WHERE store_id = ? ORDER BY name", (store_id,)
    )}
    checks = connection.execute("""
        SELECT b.* FROM backup_checks b JOIN critical_responsibilities r ON r.id = b.responsibility_id
        WHERE r.store_id = ? ORDER BY b.observed_on DESC, b.id DESC
    """, (store_id,))
    seen = set()
    for check in checks:
        entry = responsibilities[check["responsibility_id"]]
        person = check["person"].casefold()
        key = entry["id"], person
        if key in seen or person == entry["primary_person"].casefold():
            continue
        seen.add(key)
        entry["backups" if check["status"] == "verified" else "unconfirmed"].append(dict(check))
    return responsibilities

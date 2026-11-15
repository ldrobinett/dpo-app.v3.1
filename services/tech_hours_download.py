"""Compare CDK booking groups against the store’s Work Log."""

import csv
import io
import re
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from services.route_download import plan_fingerprint


CDK_HEADERS = (
    "RO-NO", "BOOKEDDATE", "CLOSEDDATE", "DT", "TECHNO", "LN", "SEQNO", "M", "HT",
    "SC", "LBRTYPE", "PAYTYPE", "ACTUALHOURS", "SOLDHOURS", "SOLDAMOUNT", "LABORCOST",
    "OP-CODE", "DESCRIPTION", "",
)
HOUR_FIELDS = ("actual", "sold")


def numbers(cells, record):
    try:
        values = [Decimal(cells[index]) for index in (12, 13)]
    except InvalidOperation:
        raise ValueError(f"Check the actual and sold hours on CSV record {record}.") from None
    if any(not value.is_finite() or not value < Decimal("1E12") or not value > Decimal("-1E12") for value in values):
        raise ValueError(f"Check the actual and sold hours on CSV record {record}.")
    return dict(zip(HOUR_FIELDS, map(str, values)))


def hour_totals(rows):
    return {
        key: sum((Decimal(row[key]) for row in rows), Decimal(0))
        if all(row[key] is not None for row in rows) else None
        for key in HOUR_FIELDS
    }


def read_tech_hours(raw):
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1252")
    reader = csv.reader(io.StringIO(text, newline=""))
    header = tuple(re.sub(r"[^A-Z0-9-]", "", value.upper()) for value in next(reader, ()))
    if header != CDK_HEADERS:
        raise ValueError("Use the CDK technician hours CSV with booked date, RO, technician, line and sequence.")
    detail, subtotals, grand = [], {}, []
    tech_rows = defaultdict(list)
    seen = set()
    current_tech = None
    for record, values in enumerate(reader, 2):
        cells = [value.strip() for value in values]
        if not any(cells):
            continue
        if len(cells) != len(CDK_HEADERS):
            raise ValueError(f"CSV record {record} has the wrong number of columns.")
        if cells[0].isascii() and cells[0].isdigit():
            ro, booked, tech, line, sequence = (cells[i] for i in (0, 1, 4, 5, 6))
            if len(ro) > 50 or len(line) > 10 or not tech.isascii() or not tech.isdigit():
                raise ValueError(f"Check the repair order, line and technician on CSV record {record}.")
            try:
                booked = datetime.strptime(booked.upper(), "%d%b%y").date().isoformat()
            except ValueError:
                raise ValueError(f"Check the booked date on CSV record {record}.") from None
            key = (booked, tech, ro, line, sequence)
            if key in seen:
                raise ValueError(f"Duplicate booking on CSV record {record}. Check the CDK export.")
            seen.add(key)
            row = dict(date=booked, tech=tech, ro=ro, line=line, sequence=sequence, record=record,
                       **numbers(cells, record))
            detail.append(row)
            tech_rows[tech].append(row)
            current_tech = tech
        elif cells[4] == "***":
            if not current_tech or current_tech in subtotals:
                raise ValueError(f"Check the technician subtotal on CSV record {record}.")
            subtotals[current_tech] = numbers(cells, record)
        elif not cells[0] and not cells[4] and any(cells[12:16]):
            grand.append(numbers(cells, record))
        elif any(value for index, value in enumerate(cells) if index != 16):
            raise ValueError(f"Unrecognized CSV record {record}. Check the CDK export.")
    if not detail or len(grand) != 1 or hour_totals(detail) != hour_totals(grand):
        raise ValueError("The CDK detail must match one grand total for actual and sold hours.")
    if set(tech_rows) != set(subtotals) or any(
        hour_totals(rows) != hour_totals([subtotals[tech]]) for tech, rows in tech_rows.items()
    ):
        raise ValueError("The technician subtotals do not match the CDK detail.")
    return detail


def compare_tech_hours(store_id, detail):
    from models import Team, TeamMember, WorkLog

    dates = {row["date"] for row in detail}
    members = TeamMember.query.join(Team).filter(Team.store_id == store_id).all()
    techs = defaultdict(list)
    for member in members:
        if member.tech_number:
            techs[member.tech_number.strip()].append(member)
    app_rows = defaultdict(list)
    source_groups = defaultdict(list)
    logs = WorkLog.query.join(TeamMember).join(Team).filter(
        Team.store_id == store_id, WorkLog.date.between(date.fromisoformat(min(dates)), date.fromisoformat(max(dates))),
    )
    for log in logs:
        booked = log.date.isoformat()
        if booked not in dates:
            continue
        key = (booked, log.team_member_id, (log.ro_number or "").strip(), (log.line_item or "").strip())
        app_rows[key].append(dict(sold=str(log.flat_rate_hours) if log.flat_rate_hours is not None else None,
                                  actual=str(log.actual_time) if log.actual_time is not None else None))
    for row in detail:
        source_groups[row["date"], row["tech"], row["ro"], row["line"]].append(row)
    members_by_booking = {}
    source_app_keys = set()
    for booked, tech, ro, line in source_groups:
        matches = [member for member in techs[tech] if not member.retired_at or
                   booked < member.retired_at.date().isoformat()]
        if len(matches) == 1:
            members_by_booking[booked, tech] = matches[0]
            source_app_keys.add((booked, matches[0].id, ro, line))
    unmatched_app_ros = {key[:3] for key in app_rows.keys() - source_app_keys}

    classified, missing = [], []
    for (booked, tech, ro, line), rows in sorted(source_groups.items()):
        member = members_by_booking.get((booked, tech))
        key = (booked, member.id, ro, line) if member else None
        recorded = app_rows.get(key)
        source = hour_totals(rows)
        app = hour_totals(recorded) if recorded else None
        issue = ""
        if member is None:
            kind, issue = "mapping", "Confirm which technician owns this CDK ID."
        elif recorded:
            kind = "match" if app == source else "different"
            if kind == "different":
                issue = "Check the CDK lines and the saved booking before changing hours."
        elif not line or key[:3] in unmatched_app_ros or any(
            Decimal(row[field]) < 0 for row in rows for field in HOUR_FIELDS
        ):
            kind, issue = "different", "Check the line or reversal against the saved work before adding hours."
        else:
            kind = "missing"
            issue = "Ready to add after review."
            missing.extend(dict(row, member_id=member.id) for row in rows)
        classified.append(compare_row(booked, ro, line, tech, member.name if member else None,
                                      kind, source, app, issue))
    names = {member.id: member for member in members}
    for (booked, member_id, ro, line), rows in sorted(app_rows.items()):
        if (booked, member_id, ro, line) in source_app_keys:
            continue
        member = names[member_id]
        classified.append(compare_row(booked, ro, line, member.tech_number, member.name, "app-only",
                                      None, hour_totals(rows), "Check whether the download includes this booking."))
    return classified, missing


def compare_row(booked, ro, line, tech, name, kind, source, app, issue):
    def display(values):
        return {key: str(value.quantize(Decimal(".01"))) if value is not None else None
                for key, value in values.items()} if values else None

    return dict(date=booked, ro=ro, line=line, tech=tech, name=name, kind=kind,
                source=display(source), app=display(app), issue=issue)


def comparison_fingerprint(results, missing):
    return plan_fingerprint([results, missing])

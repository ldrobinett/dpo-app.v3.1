"""Preview a CDK route-sheet download without inferring closed repair orders."""

import csv
import hashlib
import io
import json
from collections import defaultdict
from datetime import datetime

CDK_STATUSES = {
    "OPENED", "AUTH. HOLD", "LINE ON HOLD", "HOLD", "PREASSIGNED", "VEH. DISABLED",
    "WORKING", "READY TO POST", "ALL LAB. POSTED", "ALL LABOR POSTED", "PRE-INVOICED", "CLOSED",
}


def read_download(raw, hide_customer=False):
    try:
        content = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        content = raw.decode("cp1252")
    # CDK can emit inconsistent quotes in free-text fields. Validate row width and
    # withhold the service text when the known layout has an extra trailing cell.
    reader = csv.reader(io.StringIO(content, newline=""))
    headers = [value.strip() for value in next(reader, ())]
    if any(headers.count(name) != 1 for name in ("RO", "Status Code Desc")):
        raise ValueError("Use a CDK Route Sheet CSV with RO and Status Code Desc columns.")
    rows = {}
    for record, values in enumerate(reader, 2):
        cells = dict(zip(headers, values))
        number = cells.get("RO", "").strip()
        if not number.isdecimal() or len(number) > 20:
            if number:
                raise ValueError(f"CSV record {record} has an invalid RO number.")
            continue
        if number in rows:
            raise ValueError(f"RO {number} appears more than once. Check the download before loading it.")
        issues = []
        extra_column = len(values) != len(headers)
        if extra_column:
            if (len(values) == len(headers) + 1 and headers.index("Status Code Desc") == 16
                    and headers.index("RO") == 6 and "Service Request" in headers):
                issues.append("Extra column. Service description left alone.")
            else:
                rows[number] = dict(issues=["Column count does not match the header. Review this row."], skip=True)
                continue
        status = cells.get("Status Code Desc", "").strip().upper()
        if status not in CDK_STATUSES:
            rows[number] = dict(issues=[f"Check CDK status: {status or 'blank'}."], skip=True)
            continue
        promise_raw = cells.get("Promise", "").strip()
        promise = None
        if promise_raw:
            for fmt in ("%m/%d/%Y %I:%M:%S %p", "%m/%d/%Y %I:%M %p", "%m/%d/%Y %H:%M"):
                try:
                    promise = datetime.strptime(promise_raw, fmt).isoformat()
                    break
                except ValueError:
                    continue
            if promise is None:
                issues.append("Check the promise time. Existing time left alone.")
        rows[number] = dict(
            status="Closed" if status == "CLOSED" else status, issues=issues, promise=promise,
            techs=cells.get("Tech", "").split(), advisor=cells.get("SA", "").strip(),
            customer=None if hide_customer else cells.get("Customer", "").strip()[:100] or None,
            vehicle=None if hide_customer else " ".join(
                cells.get(name, "").strip() for name in ("Year", "Model")
            ).strip()[:100] or None,
            service=None if hide_customer or extra_column
            else cells.get("Service Request", "").strip() or None,
        )
    if not rows:
        raise ValueError("The download contains no repair orders.")
    return rows


def preview_download(store_id, imported):
    from models import ASM, RepairOrder, Team, TeamMember

    existing = {ro.ro_number: ro for ro in RepairOrder.query.filter_by(store_id=store_id)}
    techs = defaultdict(list)
    advisors = defaultdict(list)
    for tech in TeamMember.query.join(Team).filter(Team.store_id == store_id, TeamMember.retired_at.is_(None)):
        if tech.tech_number:
            techs[tech.tech_number].append(tech)
    for advisor in ASM.query.filter_by(store_id=store_id):
        if advisor.asm_number:
            advisors[advisor.asm_number].append(advisor)
    plan = []
    for number, row in imported.items():
        current = existing.get(number)
        issues = list(row["issues"])
        if row.get("skip"):
            plan.append(dict(ro=number, kind="Skipped", issues=issues, changes={}, before={}))
            continue
        status = row["status"]
        if current and (current.status or "").upper() == "CLOSED" and status != "Closed":
            plan.append(dict(ro=number, kind="Skipped", issues=issues + [
                "Already closed in ProdTracker. Confirm before reopening."
            ], changes={}, before={}))
            continue
        values = {
            "status": status, "promised_time": row["promise"], "customer_name": row["customer"],
            "vehicle_info": row["vehicle"], "service_description": row["service"],
        }
        names = {}
        matching = techs.get(row["techs"][0], []) if len(row["techs"]) == 1 else []
        if len(matching) == 1:
            values["team_member_id"] = matching[0].id
            names["team_member_id"] = matching[0].name
        elif row["techs"]:
            issues.append("Check technician assignment: " + ", ".join(row["techs"]))
        elif status != "Closed":
            issues.append("No technician listed in the download.")
        if row["advisor"]:
            matching = advisors.get(row["advisor"], [])
            if len(matching) == 1:
                values["asm_id"] = matching[0].id
                names["asm_id"] = matching[0].name
            else:
                issues.append(f"Check ASM assignment: {row['advisor']}.")

        before = {}
        changes = {}
        for name, value in values.items():
            if value is None:
                continue
            prior = getattr(current, name) if current else None
            if isinstance(prior, datetime):
                prior = prior.isoformat()
            if value != prior:
                before[name] = prior
                changes[name] = value
        kind = "New" if current is None else "Updated" if changes else "No change"
        plan.append(dict(ro=number, kind=kind, issues=issues, changes=changes, before=before, names=names))
    for number, ro in sorted(existing.items()):
        if number not in imported and (ro.status or "").upper() != "CLOSED":
            plan.append(dict(ro=number, kind="Missing from file", changes={}, before={}, issues=[
                "Still open in ProdTracker. Confirm the RO status."
            ]))
    return plan, existing


def plan_fingerprint(plan):
    return hashlib.sha256(json.dumps(plan, sort_keys=True).encode("utf-8")).hexdigest()

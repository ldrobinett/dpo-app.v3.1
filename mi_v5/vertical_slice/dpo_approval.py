"""Non-executable DPO proposals with canonical, department-scoped authority."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date, datetime, time, timezone
from uuid import UUID
from zoneinfo import ZoneInfo

from mi_v5.schema_versions import (
    ASSIGNMENT_REVISION, DPO_AUTHORIZATION_CAPABILITY, ISOLATED_V5_DATABASE,
)
from mi_v5.vertical_slice.dpo_governance import _calculated_dpo

HISTORY_FIELDS = (
    "hist_frh_total", "hist_days_in_period", "hist_training_days",
    "hist_vacation_days", "expected_lift_percent",
)
_ASSIGNMENT_STATES = {"pending", "active", "completed", "cancelled"}


def _identity(value):
    try:
        return str(UUID(str(value))) if value is not None else None
    except (ValueError, TypeError, AttributeError):
        return None


def _timestamp(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00")) \
        if isinstance(value, str) else value
    if not isinstance(parsed, datetime) or parsed.utcoffset() is None:
        raise ValueError("Timezone-aware timestamp required")
    return parsed


def _period(row):
    if "effective_to" not in row:
        raise ValueError("Explicit effective end or null required")
    start = _timestamp(row.get("effective_from"))
    end = _timestamp(row["effective_to"]) if row.get("effective_to") is not None else None
    if end is not None and end <= start:
        raise ValueError("Effective end must be strictly after start")
    return start, end


def assignment_issues(assignment: dict, existing=()) -> list[str]:
    """Validate a proposed canonical relationship without writing it."""
    issues = []
    for key in ("enterprise_id", "employee_id", "role_id", "department_id"):
        if _identity(assignment.get(key)) is None:
            issues.append(f"Assignment {key} requires an explicit UUID")
    if assignment.get("status") not in _ASSIGNMENT_STATES:
        issues.append("Assignment lifecycle state is invalid")
    if not isinstance(assignment.get("is_primary"), bool):
        issues.append("Assignment is_primary requires an explicit boolean")
    if assignment.get("status") == "active" and (
        not str(assignment.get("source_reference") or "").strip()
        or _identity(assignment.get("created_by_id")) is None
    ):
        issues.append("Active Assignment requires a reviewed source and audit actor")
    try:
        start, end = _period(assignment)
    except (ValueError, TypeError):
        return issues + ["Assignment requires a valid explicit effective period"]
    for previous in existing:
        same_id = _identity(previous.get("assignment_id")) == \
            _identity(assignment.get("assignment_id"))
        if same_id and _identity(assignment.get("assignment_id")) is not None:
            if previous.get("status") != "pending" and previous != assignment:
                issues.append("Published Assignment requires append-only correction")
            continue
        if any(_identity(previous.get(key)) != _identity(assignment.get(key))
               for key in ("enterprise_id", "role_id", "department_id")):
            continue
        try:
            previous_start, previous_end = _period(previous)
        except (ValueError, TypeError):
            issues.append("Existing Assignment period is invalid")
            continue
        if (_identity(previous.get("employee_id")) == _identity(assignment.get("employee_id"))
                and previous_start == start):
            issues.append("Duplicate Assignment effective identity")
        if (assignment.get("is_primary") is True
                and previous.get("is_primary") is True
                and assignment.get("status") in {"pending", "active"}
                and previous.get("status") in {"pending", "active"}
                and (end is None or previous_start < end)
                and (previous_end is None or start < previous_end)):
            issues.append("Overlapping exclusive primary Role/context assignments")
    return issues


def source_fingerprint(snapshot: dict) -> str:
    """Bind review to the exact active technician set and raw inputs."""
    material = {
        "scope": {key: str(snapshot["scope"][key]) for key in (
            "enterprise_id", "managed_store_id", "department_id"
        )},
        "technicians": sorted(
            ({key: row.get(key) for key in (
                "id", "tech_number", "daily_production_objective",
                "dpo_calculation_mode", *HISTORY_FIELDS,
            )} for row in snapshot["technicians"]),
            key=lambda row: row["id"],
        ),
    }
    encoded = json.dumps(
        material, sort_keys=True, separators=(",", ":"), default=str, allow_nan=False
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _one(rows, key, identifier, label, issues):
    matches = [row for row in rows if _identity(row.get(key)) == identifier]
    if identifier is None or len(matches) != 1:
        issues.append(f"{label} requires one existing explicitly reviewed record")
        return None
    return matches[0]


def _active_entity(row, enterprise, label, issues):
    if (_identity(row.get("enterprise_id")) != enterprise
            or "retired_at" not in row
            or row.get("status") != "active" or row.get("retired_at") is not None):
        issues.append(f"{label} must be active, non-retired and in the requested tenant")


def _window(row, instants, label, issues):
    try:
        start, end = _period(row)
        if any(at < start or (end is not None and at >= end) for at in instants):
            issues.append(f"{label} is outside its effective period")
    except (ValueError, TypeError):
        issues.append(f"{label} has a missing or invalid timezone-aware period")


def _existing_operation(record, existing):
    relevant = [row for row in existing
                if row.get("legacy_team_member_id") == record["legacy_team_member_id"]]
    for row in relevant:
        if any(str(row.get(key)) != str(record[key])
               for key in ("enterprise_id", "managed_store_id", "department_id")):
            raise ValueError("Existing DPO belongs to another tenant/store/department")
    start = date.fromisoformat(record["effective_from"])
    same_start = [row for row in relevant
                  if str(row["effective_from"]) == record["effective_from"]]
    if len(same_start) > 1:
        raise ValueError("Duplicate existing DPO effective identity")
    open_records = [row for row in relevant if row.get("effective_to") is None]
    if len(open_records) > 1:
        raise ValueError("Ambiguous current DPO")
    if same_start:
        old = same_start[0]
        end = date.fromisoformat(record["effective_to"]) \
            if record["effective_to"] is not None else None
        for row in relevant:
            if row is old:
                continue
            other_start = date.fromisoformat(str(row["effective_from"]))
            other_end = date.fromisoformat(str(row["effective_to"])) \
                if row.get("effective_to") is not None else None
            # DPO date ranges include both endpoints, unlike Assignment timestamps.
            if ((end is None or other_start <= end)
                    and (other_end is None or start <= other_end)):
                raise ValueError("Existing DPO history overlaps the proposed period")
        keys = (
            "dpo_value", "calculation_mode", "calculated_dpo", "is_override",
            "authority_status", "authorized_by_id", "authorization_reason",
            "source_reference",
        )
        same = all(str(old.get(key)) == str(record.get(key)) for key in keys)
        same = same and (
            (str(old.get("effective_to")) if old.get("effective_to") is not None else None)
            == record["effective_to"]
        )
        same = same and json.loads(old["calculation_inputs_json"]) == \
            json.loads(record["calculation_inputs_json"])
        if not same:
            raise ValueError("Conflicting existing DPO at the same effective start")
        return {"operation": "unchanged"}
    if any(date.fromisoformat(str(row["effective_from"])) >= start for row in relevant):
        raise ValueError("DPO proposals must move forward in effective time")
    if any(row.get("effective_to") is not None
           and date.fromisoformat(str(row["effective_to"])) >= start for row in relevant):
        raise ValueError("Existing bounded DPO overlaps the proposed period")
    if open_records:
        from datetime import timedelta
        return {
            "operation": "supersede",
            "prior_record_id": str(open_records[0]["technician_dpo_record_id"]),
            "close_prior_at": (start - timedelta(days=1)).isoformat(),
        }
    return {"operation": "insert"}


def build_proposal(snapshot: dict, review: dict, *, now: datetime) -> dict:
    """Validate persisted evidence and explicit review; never authorize or apply."""
    now = _timestamp(now)
    if not isinstance(review, dict):
        raise ValueError("Human review must be a JSON object")
    if snapshot.get("database") != ISOLATED_V5_DATABASE:
        raise ValueError("Only the isolated dpo_v5_beta database is supported")
    if snapshot.get("migration") != ASSIGNMENT_REVISION:
        raise ValueError("Canonical Assignment migration is required")
    scope = snapshot["scope"]
    expected = {
        "enterprise_name": "AutoNation", "store_name": "Honda Renton",
        "store_code": "HONDA_RENTON", "external_reference": "legacy_managed_store:2",
        "department_code": "SERVICE", "department_type": "service",
    }
    if any(scope.get(key) != value for key, value in expected.items()):
        raise ValueError("Exact Honda Renton Service scope is required")
    scope_ids = {key: _identity(scope.get(key)) for key in (
        "enterprise_id", "managed_store_id", "department_id"
    )}
    if any(value is None for value in scope_ids.values()):
        raise ValueError("Canonical scope identities are invalid")
    issues = []
    if "apply" in review:
        issues.append("Apply is unsupported; this surface is a non-executable preview")
    for key, value in scope_ids.items():
        if _identity(review.get(key)) != value:
            issues.append(f"Explicit reviewed {key} must match the canonical scope")
    for label in ("enterprise", "store", "department"):
        if f"{label}_retired_at" not in scope \
                or scope.get(f"{label}_status") != "active" \
                or scope.get(f"{label}_retired_at") is not None:
            issues.append(f"Canonical {label} is inactive or retired")
    requested_date = None
    requested_end = None
    try:
        requested_date = date.fromisoformat(review.get("effective_from", ""))
        if requested_date < now.astimezone(ZoneInfo("America/Los_Angeles")).date():
            issues.append("DPO effective date must be prospective in America/Los_Angeles")
        if "effective_to" not in review:
            issues.append("Explicit reviewed DPO effective_to is required, including null")
        elif review["effective_to"] is not None:
            requested_end = date.fromisoformat(review["effective_to"])
            if requested_end < requested_date:
                issues.append("DPO effective end precedes its start")
    except (ValueError, TypeError):
        issues.append("Explicit reviewed DPO effective date is required")
    instants = [now]
    if requested_date is not None:
        instants.append(datetime.combine(
            requested_date, time.min, tzinfo=ZoneInfo("America/Los_Angeles")
        ).astimezone(timezone.utc))
    if any(key not in scope for key in (
        "department_effective_from", "department_effective_to"
    )):
        issues.append("Department effective period is unknown")
    _window({
        "effective_from": scope.get("department_effective_from"),
        "effective_to": scope.get("department_effective_to"),
    }, instants, "Department", issues)
    identifiers = {key: _identity(review.get(key)) for key in (
        "authorized_by_id", "role_id", "assignment_id", "role_capability_id",
    )}
    employee = _one(snapshot["employees"], "employee_id",
                    identifiers["authorized_by_id"], "Approving Employee", issues)
    role = _one(snapshot["roles"], "role_id", identifiers["role_id"], "SM Role", issues)
    assignment = _one(snapshot["assignments"], "assignment_id",
                      identifiers["assignment_id"], "Canonical Assignment", issues)
    grant = _one(snapshot["role_grants"], "role_capability_id",
                 identifiers["role_capability_id"], "Role capability grant", issues)
    enterprise = scope_ids["enterprise_id"]
    if employee:
        _active_entity(employee, enterprise, "Employee", issues)
    if role:
        _active_entity(role, enterprise, "Role", issues)
        _window(role, instants, "Role", issues)
    if assignment:
        issues.extend(assignment_issues(assignment, snapshot["assignments"]))
        if (_identity(assignment.get("enterprise_id")) != enterprise
                or _identity(assignment.get("employee_id")) != identifiers["authorized_by_id"]
                or _identity(assignment.get("role_id")) != identifiers["role_id"]
                or _identity(assignment.get("department_id")) != scope_ids["department_id"]
                or assignment.get("status") != "active"):
            issues.append("Assignment does not authorize this Employee/Role/department")
        if assignment.get("effective_to") is None:
            issues.append("Isolated test Assignment requires an explicit bounded end")
        _window(assignment, instants, "Assignment", issues)
        creator = _one(snapshot["employees"], "employee_id",
                       _identity(assignment.get("created_by_id")), "Assignment audit actor", issues)
        if creator and _identity(creator.get("enterprise_id")) != enterprise:
            issues.append("Assignment audit actor belongs to another tenant")
    if grant:
        if (_identity(grant.get("enterprise_id")) != enterprise
                or _identity(grant.get("role_id")) != identifiers["role_id"]):
            issues.append("Capability grant belongs to another tenant or Role")
        _window(grant, instants, "Role capability grant", issues)
        capability = _one(snapshot["capabilities"], "capability_id",
                          _identity(grant.get("capability_id")), "Capability", issues)
        if capability:
            _active_entity(capability, enterprise, "Capability", issues)
            _window(capability, instants, "Capability", issues)
            if capability.get("key") != DPO_AUTHORIZATION_CAPABILITY:
                issues.append("Exact dpo.authorize capability is required")
    fingerprint = source_fingerprint(snapshot)
    if review.get("source_fingerprint") != fingerprint:
        issues.append("Explicit review must match the current technician source fingerprint")
    raw_reference = review.get("approval_reference")
    approval_reference = raw_reference.strip() if isinstance(raw_reference, str) else ""
    if not approval_reference:
        issues.append("Explicit human approval_reference is required")
    if review.get("authority_status") != "provisional":
        issues.append("This isolated test requires explicitly reviewed provisional authority")
    source_reference = None
    if approval_reference and all(identifiers[key] for key in (
        "assignment_id", "role_capability_id"
    )):
        source_reference = (
            f"{approval_reference};assignment={identifiers['assignment_id']};"
            f"grant={identifiers['role_capability_id']}"
        )
        if len(source_reference) > 255:
            issues.append("Approval and authority source reference exceeds 255 characters")
            source_reference = None
    approvals = {}
    review_items = review.get("approvals", [])
    if not isinstance(review_items, list):
        raise ValueError("Technician approvals must be a JSON array of objects")
    for item in review_items:
        if not isinstance(item, dict):
            issues.append("Each technician approval requires an explicit JSON object")
            continue
        member = item.get("legacy_team_member_id")
        if not isinstance(member, int) or isinstance(member, bool) or member in approvals:
            issues.append("Technician approvals require unique explicit member identities")
            continue
        approvals[member] = item
    members = [row["id"] for row in snapshot["technicians"]]
    if len(set(members)) != len(members):
        issues.append("Duplicate technician source identity")
    if not members:
        issues.append("No active technicians found")
    if set(approvals) - set(members):
        issues.append("Approval includes technicians outside the active store set")
    records = []
    for row in snapshot["technicians"]:
        inputs = {key: row.get(key) for key in HISTORY_FIELDS}
        approved = approvals.get(row["id"], {})
        value = approved.get("approved_value")
        raw_reason = approved.get("reason")
        reason = raw_reason.strip() or None if isinstance(raw_reason, str) else None
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value) or value <= 0):
            issues.append(f"Technician {row['id']} requires an explicit positive reviewed value")
            value = None
        if not reason:
            issues.append(f"Technician {row['id']} requires an explicit human reason")
        if not str(row.get("tech_number") or "").strip():
            issues.append(f"Technician {row['id']} has no technician number")
        mode = row.get("dpo_calculation_mode")
        if mode not in {"manual", "calculated"}:
            issues.append(f"Technician {row['id']} has an unsupported calculation mode")
        calculated = _calculated_dpo(inputs)
        if mode == "calculated" and value is not None and value != calculated:
            issues.append(f"Technician {row['id']} cannot disguise an override as calculated")
        record = {
            "technician_dpo_record_id": None, **scope_ids,
            "legacy_team_member_id": row["id"],
            "effective_from": requested_date.isoformat() if requested_date else None,
            "effective_to": requested_end.isoformat() if requested_end else None,
            "dpo_value": value, "calculation_mode": mode,
            "calculated_dpo": calculated, "is_override": mode != "calculated",
            "authority_status": "provisional",
            "authorized_by_id": identifiers["authorized_by_id"],
            "authorization_reason": reason,
            "calculation_inputs_json": json.dumps(inputs, sort_keys=True),
            "source_reference": source_reference,
            "created_at": None, "created_by_id": identifiers["authorized_by_id"],
            "updated_at": None, "updated_by_id": None, "version": None,
        }
        warnings = []
        if tuple(inputs.values()) == (80.0, 10, 0, 0, 100.0):
            warnings.append("Legacy defaults match; provenance unverified, not proof of fabricated history")
        records.append({
            "candidate_manual_value": row["daily_production_objective"],
            "calculation_warnings": warnings, "record": record,
            "planned_change": {"operation": "blocked"},
        })
    if not issues:
        for item in records:
            try:
                item["planned_change"] = _existing_operation(
                    item["record"], snapshot["existing_dpos"]
                )
            except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
                issues.append(str(exc))
    if issues:
        for item in records:
            item["planned_change"] = {"operation": "blocked"}
    return {
        "mode": "dry_run", "database": ISOLATED_V5_DATABASE,
        "schema_revision": ASSIGNMENT_REVISION,
        "test_only": True, "apply_available": False,
        "future_apply_requires_transactional_revalidation": True,
        "authority_created": False, "historical_dpo_verified": False,
        "blocked": bool(issues), "blocking_issues": issues,
        "required_capability": DPO_AUTHORIZATION_CAPABILITY,
        "source_fingerprint": fingerprint, "technician_count": len(records),
        "canonical_employee_count": len({
            _identity(row.get("employee_id")) for row in snapshot["employees"]
            if _identity(row.get("enterprise_id")) == enterprise
            and _identity(row.get("employee_id")) is not None
        }),
        "existing_governed_records": len(snapshot["existing_dpos"]),
        "proposed_records": records,
        "limitations": [
            "Preview only; no apply or identity/grant creation path.",
            "Future apply must re-read and lock persisted authority and source in its transaction.",
            "Finite primary overlap is validated here; PostgreSQL concurrency is not established.",
        ],
    }

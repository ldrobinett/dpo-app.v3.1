"""Plan bounded recurring schedules without database writes."""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import timedelta


@dataclass
class SchedulePlan:
    creates: list = field(default_factory=list)
    updates: list = field(default_factory=list)
    deletes: list = field(default_factory=list)
    unchanged: int = 0
    protected: int = 0


def plan_recurring_schedule(
    member_ids, existing_entries, start_date, end_date, days_of_week,
    holidays, shift_values, *, replace=False,
):
    """Replace only ordinary WORK rows; unknown types fail safe as exceptions.

    Callers must authorize/lock the target members and apply this plan in one
    transaction. Existing rows are never mutated during planning.
    """
    if end_date < start_date:
        raise ValueError("End date must be on or after start date.")
    selected_days = set(days_of_week)
    if not selected_days or not selected_days.issubset(set(range(7))):
        raise ValueError("Select at least one valid weekday.")
    member_ids = sorted(set(member_ids))
    by_day = defaultdict(list)
    for entry in existing_entries:
        if entry.team_member_id not in member_ids or not start_date <= entry.date <= end_date:
            raise ValueError("Schedule entry is outside the selected scope.")
        by_day[(entry.team_member_id, entry.date)].append(entry)
    if replace and any(len(rows) > 1 for rows in by_day.values()):
        raise ValueError(
            "Multiple entries exist for a technician on the same date. "
            "Review those entries in Manage PTO / Training before replacing schedules."
        )

    plan = SchedulePlan()
    day = start_date
    while day <= end_date:
        selected = day.weekday() in selected_days
        for member_id in member_ids:
            rows = by_day.get((member_id, day), [])
            if rows and not replace:
                plan.protected += sum(row.schedule_type != "WORK" for row in rows)
                plan.unchanged += sum(row.schedule_type == "WORK" for row in rows)
                continue
            row = rows[0] if rows else None
            if row is not None and row.schedule_type != "WORK":
                plan.protected += 1
                continue
            if not selected:
                if row is not None:
                    plan.deletes.append(row)
                continue

            values = dict(shift_values)
            values["schedule_type"] = "WORK"
            if day in holidays:
                values.update(
                    start_time=None, end_time=None, lunch_start=None,
                    lunch_end=None, notes="Shop Holiday", schedule_type="HOLIDAY",
                )
            if row is None:
                plan.creates.append(dict(values, team_member_id=member_id, date=day))
            elif any(getattr(row, key) != value for key, value in values.items()):
                plan.updates.append((row, values))
            else:
                plan.unchanged += 1
        if day == end_date:
            break
        day += timedelta(days=1)
    return plan

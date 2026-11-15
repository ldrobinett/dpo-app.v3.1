"""Shop-floor pace from recorded shifts and Work Log bookings."""

from collections import defaultdict
from math import isfinite


def seconds(value):
    return value.hour * 3600 + value.minute * 60 + value.second


def working_intervals(shifts):
    intervals = []
    for shift in shifts:
        if shift.start_time is None or shift.end_time is None or shift.start_time >= shift.end_time:
            return None
        start, end = seconds(shift.start_time), seconds(shift.end_time)
        if shift.lunch_start is None and shift.lunch_end is None:
            intervals.append((start, end))
        elif shift.lunch_start and shift.lunch_end and shift.start_time <= shift.lunch_start < shift.lunch_end <= shift.end_time:
            intervals.extend(((start, seconds(shift.lunch_start)), (seconds(shift.lunch_end), end)))
        else:
            return None

    merged = []
    for start, end in sorted(intervals):
        if start == end:
            continue
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged or None


def shop_production_today(now, shifts, logs, targets_verified):
    booked = sum(float(log.flat_rate_hours) for log in logs) if logs else None
    work = defaultdict(list)
    for shift in shifts:
        retired = shift.team_member.retired_at
        if shift.schedule_type == "WORK" and (not retired or shift.date < retired.date()):
            work[shift.team_member_id].append(shift)
    result = dict(booked=booked, target=None, expected=None, scheduled=len(work),
                  status="Target unavailable", tone="neutral")

    if not work:
        result["reason"] = "No work shifts entered for today."
        return result
    if not targets_verified:
        result["reason"] = "Confirm the shop’s DPOs before using a target."
        return result
    objectives = {}
    intervals = {}
    for member_id, entries in work.items():
        member = entries[0].team_member
        dpo = member.calculated_dpo if member.dpo_calculation_mode == "calculated" else member.daily_production_objective
        if dpo is None or dpo <= 0 or not isfinite(dpo):
            result["reason"] = "Enter a DPO for each scheduled technician."
            return result
        objectives[member_id] = dpo
        intervals[member_id] = working_intervals(entries)
    target = sum(objectives.values())
    result.update(target=target, status="Pace unavailable")
    if booked is None:
        result["reason"] = "No Work Log bookings for today yet."
    elif any(log.team_member_id not in work for log in logs):
        result["reason"] = "Some hours were booked by techs without a work shift. Check the schedule."
    elif booked >= target:
        result.update(status="Target reached", tone="good", reason="Today’s booked hours meet the full-shift target.")
    elif any(not slots for slots in intervals.values()):
        result["reason"] = "Check today’s shift and lunch times."
    else:
        current = seconds(now.time())
        expected = 0.0
        for member_id, slots in intervals.items():
            total_time = sum(end - start for start, end in slots)
            elapsed = sum(max(0, min(end, current) - start) for start, end in slots)
            expected += objectives[member_id] * elapsed / total_time
        result["expected"] = expected
        if expected <= 0:
            result.update(status="Before first shift", reason="Pace starts when the scheduled work begins.")
        elif round(booked, 2) >= round(expected, 2):
            result.update(status="On pace", tone="good", reason="Booked hours meet the target for this point in the shift.")
        else:
            result.update(status="Behind pace", tone="attention", reason="Booked hours are below the target for this point in the shift.")
    return result

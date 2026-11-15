"""Booked-hour shares for the selected technician population."""

import math


def booked_hour_shares(hours_by_technician):
    hours = list(hours_by_technician)
    total = sum(hours)
    if not math.isfinite(total) or total <= 0 or any(value < 0 for value in hours):
        return [None] * len(hours)
    return [value / total * 100 for value in hours]

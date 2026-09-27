"""Lifecycle states for an accountable Management Action."""

from enum import Enum


class ManagementActionStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

"""Lifecycle states for Management Intelligence v5 teams."""

from enum import StrEnum


class TeamStatus(StrEnum):
    """Lifecycle state of an optional execution team."""

    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"
    RETIRED = "retired"

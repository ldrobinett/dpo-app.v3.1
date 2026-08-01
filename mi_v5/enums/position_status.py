"""Lifecycle states for a canonical organizational Position."""

from enum import Enum


class PositionStatus(str, Enum):
    """Whether a budgeted organizational position can receive assignments."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    FROZEN = "frozen"
    ELIMINATED = "eliminated"
    RETIRED = "retired"

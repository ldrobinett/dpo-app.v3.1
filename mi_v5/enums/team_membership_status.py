"""Lifecycle states for an MI v5 Team Membership."""

from enum import Enum


class TeamMembershipStatus(str, Enum):
    """Current lifecycle state of an employee's Team membership."""

    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

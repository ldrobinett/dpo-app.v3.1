"""Department lifecycle states."""

from enum import Enum


class DepartmentStatus(str, Enum):
    """Valid lifecycle states for a Department."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"
    RETIRED = "retired"

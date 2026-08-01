"""Employment lifecycle states for Management Intelligence v5."""

from enum import Enum


class EmployeeStatus(str, Enum):
    """Current employment relationship with one Enterprise tenant."""

    PENDING = "pending"
    ACTIVE = "active"
    LEAVE = "leave"
    TERMINATED = "terminated"
    RETIRED = "retired"

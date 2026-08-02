"""Lifecycle states for an Employee Assignment."""

try:
    from enum import StrEnum
except ImportError:  # pragma: no cover - compatibility fallback
    from enum import Enum

    class StrEnum(str, Enum):
        """String enum fallback for Python versions before 3.11."""


class EmployeeAssignmentStatus(StrEnum):
    """Governed lifecycle states for an employee-to-position assignment."""

    PENDING = "pending"
    ACTIVE = "active"
    LEAVE = "leave"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

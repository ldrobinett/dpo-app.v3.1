"""Organizational Group lifecycle states."""

try:
    from enum import StrEnum
except ImportError:  # pragma: no cover
    from enum import Enum

    class StrEnum(str, Enum):
        """Compatibility fallback for Python versions before 3.11."""


class OrganizationalGroupStatus(StrEnum):
    """Valid lifecycle states for an Organizational Group."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    RETIRED = "retired"

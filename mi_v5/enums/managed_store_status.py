"""Managed Store lifecycle states."""

try:
    from enum import StrEnum
except ImportError:  # pragma: no cover - compatibility for Python < 3.11
    from enum import Enum

    class StrEnum(str, Enum):
        """Compatibility implementation of enum.StrEnum."""


class ManagedStoreStatus(StrEnum):
    """Valid lifecycle states for a Managed Store."""

    PROVISIONING = "provisioning"
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"
    RETIRED = "retired"

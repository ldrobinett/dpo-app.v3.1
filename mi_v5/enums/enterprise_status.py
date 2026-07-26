"""Enterprise lifecycle states."""

from enum import StrEnum


class EnterpriseStatus(StrEnum):
    """Valid lifecycle states for an Enterprise tenant."""

    PROVISIONING = "provisioning"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    RETIRED = "retired"

"""Enterprise lifecycle states."""

from enum import Enum


class EnterpriseStatus(str, Enum):
    """Valid lifecycle states for an Enterprise tenant."""

    PROVISIONING = "provisioning"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    RETIRED = "retired"

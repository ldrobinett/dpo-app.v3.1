"""Lifecycle states for canonical MI v5 capabilities."""

from enum import Enum


class CapabilityStatus(str, Enum):
    """Lifecycle state of a reusable business capability."""

    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    RETIRED = "retired"

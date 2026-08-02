"""Lifecycle states for canonical Management Intelligence roles."""

from enum import StrEnum


class RoleStatus(StrEnum):
    """Governed lifecycle of a reusable responsibility and authority role."""

    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    RETIRED = "retired"

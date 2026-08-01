"""Canonical Department types."""

from enum import Enum


class DepartmentType(str, Enum):
    """Common dealership department classifications."""

    SERVICE = "service"
    PARTS = "parts"
    SALES = "sales"
    FINANCE = "finance"
    COLLISION = "collision"
    RECONDITIONING = "reconditioning"
    ADMINISTRATION = "administration"
    OTHER = "other"

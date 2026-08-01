"""Supported organizational grouping types."""

try:
    from enum import StrEnum
except ImportError:  # pragma: no cover
    from enum import Enum

    class StrEnum(str, Enum):
        """Compatibility fallback for Python versions before 3.11."""


class OrganizationalGroupType(StrEnum):
    """Industry-neutral organizational hierarchy labels."""

    MARKET = "market"
    REGION = "region"
    DISTRICT = "district"
    DIVISION = "division"
    PLATFORM = "platform"
    BRAND_GROUP = "brand_group"
    OWNERSHIP_GROUP = "ownership_group"
    OPERATING_CLUSTER = "operating_cluster"
    CUSTOM = "custom"

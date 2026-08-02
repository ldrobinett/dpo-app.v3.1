"""Business classifications for Management Intelligence v5 teams."""

from enum import StrEnum


class TeamType(StrEnum):
    """Purpose-oriented classification of an optional execution team."""

    LEADERSHIP = "leadership"
    OPERATIONS = "operations"
    SERVICE = "service"
    PARTS = "parts"
    SALES = "sales"
    TECHNICIAN = "technician"
    PROJECT = "project"
    EXECUTIVE = "executive"
    CROSS_FUNCTIONAL = "cross_functional"
    CUSTOM = "custom"

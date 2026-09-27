"""Lifecycle states for an advisory Recommendation Output."""

from enum import Enum


class RecommendationStatus(str, Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    SUPERSEDED = "superseded"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"

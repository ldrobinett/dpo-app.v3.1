"""Lifecycle states for an advisory Recommendation Output."""

from enum import Enum


class RecommendationStatus(str, Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    WITHDRAWN = "withdrawn"

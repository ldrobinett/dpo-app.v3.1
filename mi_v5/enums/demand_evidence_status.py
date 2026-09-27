"""Governed supported-demand evidence states."""

from enum import Enum


class DemandEvidenceStatus(str, Enum):
    SUPPORTED = "supported"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"

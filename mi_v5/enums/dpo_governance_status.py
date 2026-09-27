"""Governance states for retained technician DPO evidence."""

from enum import Enum


class DPOGovernanceStatus(str, Enum):
    VERIFIED = "verified"
    PROVISIONAL = "provisional"
    UNVERIFIED_LEGACY = "unverified_legacy"

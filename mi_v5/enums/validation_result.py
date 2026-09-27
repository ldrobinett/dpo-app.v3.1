"""Governed classifications for expected-versus-observed Validation."""

from enum import Enum


class ValidationResult(str, Enum):
    ACHIEVED = "achieved"
    PARTIALLY_ACHIEVED = "partially_achieved"
    NOT_ACHIEVED = "not_achieved"
    INCONCLUSIVE = "inconclusive"
    INVALIDATED = "invalidated"

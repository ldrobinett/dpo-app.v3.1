"""Observation-only classifications for a recorded Outcome."""

from enum import Enum


class OutcomeClassification(str, Enum):
    FAVORABLE = "favorable"
    NEUTRAL = "neutral"
    UNFAVORABLE = "unfavorable"
    INCONCLUSIVE = "inconclusive"

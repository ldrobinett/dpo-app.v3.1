"""Human dispositions for a Management Decision."""

from enum import Enum


class DecisionDisposition(str, Enum):
    ACCEPT = "accept"
    MODIFY = "modify"
    REJECT = "reject"
    DEFER = "defer"
    INDEPENDENT = "independent"

"""Membership types for an MI v5 Team."""

from enum import Enum


class TeamMembershipType(str, Enum):
    """The capacity in which an Employee participates on a Team."""

    MEMBER = "member"
    LEADER = "leader"
    COORDINATOR = "coordinator"
    CONTRIBUTOR = "contributor"
    ADVISOR = "advisor"
    OBSERVER = "observer"

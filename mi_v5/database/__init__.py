"""Shared persistence foundation for Management Intelligence v5."""

from .entities import MIEntity, TenantEntity
from .mixins import (
    AuditMixin,
    EffectiveDateMixin,
    SoftRetirementMixin,
    StatusMixin,
    TenantMixin,
    UUIDPrimaryKeyMixin,
    VersionMixin,
)
from .naming import NAMING_CONVENTION
from .types import UUID_TYPE, new_uuid

__all__ = [
    "AuditMixin",
    "EffectiveDateMixin",
    "MIEntity",
    "NAMING_CONVENTION",
    "SoftRetirementMixin",
    "StatusMixin",
    "TenantEntity",
    "TenantMixin",
    "UUIDPrimaryKeyMixin",
    "UUID_TYPE",
    "VersionMixin",
    "new_uuid",
]

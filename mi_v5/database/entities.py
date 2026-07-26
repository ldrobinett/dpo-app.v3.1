"""Abstract persisted entities for Management Intelligence v5.

These classes provide the common SQLAlchemy foundation for MI v5 business
entities while continuing to use the application's existing Flask-SQLAlchemy
``db`` instance and metadata.
"""

from extensions import db

from .mixins import (
    AuditMixin,
    TenantMixin,
    UUIDPrimaryKeyMixin,
    VersionMixin,
)


class MIEntity(UUIDPrimaryKeyMixin, AuditMixin, VersionMixin, db.Model):
    """Base for persisted MI v5 records that are not necessarily tenant-owned."""

    __abstract__ = True


class TenantEntity(TenantMixin, MIEntity):
    """Base for all persisted records owned by an Enterprise tenant."""

    __abstract__ = True

"""Abstract SQLAlchemy bases for Management Intelligence v5 models."""

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
    """Base for all records owned by an Enterprise tenant."""

    __abstract__ = True

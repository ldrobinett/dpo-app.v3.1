"""Shared database types and identity generation."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import Uuid

UUID_TYPE = Uuid(as_uuid=True)


def new_uuid() -> UUID:
    """Return a portable UUID primary key.

    UUIDv4 is used until the runtime provides a stable UUIDv7 implementation.
    The callable is centralized so the strategy can change without touching models.
    """

    return uuid4()

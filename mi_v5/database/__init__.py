"""Shared persistence foundation for Management Intelligence v5.

Import concrete persistence components directly from their modules.
Keeping this package initializer lightweight prevents circular imports
while the Flask SQLAlchemy extension is being created.
"""

__all__: list[str] = []
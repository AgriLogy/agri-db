"""SQLAlchemy declarative base shared by every agri.db ORM module.

SQLAlchemy 2.0 style — uses ``DeclarativeBase`` instead of
``declarative_base()``. Includes two helpers that every model inherits:

  * ``to_dict(exclude=...)`` — column-name → value mapping; useful for
    serializing to JSON / caching.
  * ``__repr__`` — sorted ``key=value`` body; useful in shells / logs.

Pattern follows the ``RevlyBase`` mixin from full-stack/data-model-main.
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class HasDeviceId:
    """Mixin adding the optional ``device_id`` soft-FK to sensor-reading tables.

    Points at ``analytics_device.id`` with NO database-level foreign key
    (matching the Django ``db_constraint=False`` convention already used for the
    device/zone relations). Ownership of a device-sourced reading is resolved by
    JOINing the reading to ``analytics_device`` at query time, so transferring a
    device to another account/zone is a single-row update on ``analytics_device``
    with no reading rewrite. Weather / ET0 / manual readings leave it NULL and
    keep resolving ownership through their own ``user_id`` / ``zone_id``.
    """

    device_id: Mapped[Optional[int]] = mapped_column(BigInteger, index=True)


class AgriBase(DeclarativeBase):
    """Root declarative base for every Agrilogy ORM model."""

    def to_dict(self, *, exclude: set[str] | None = None) -> dict[str, Any]:
        exclude = exclude or set()
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.c
            if c.name not in exclude
        }

    def __repr__(self) -> str:
        keys = sorted(k for k in self.__dict__ if not k.startswith("_"))
        body = ", ".join(f"{k}={self.__dict__[k]!r}" for k in keys)
        return f"<{self.__class__.__name__}({body})>"

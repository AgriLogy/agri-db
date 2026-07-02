"""SQLAlchemy declarative base shared by every agri.db ORM module.

SQLAlchemy 2.0 style — uses ``DeclarativeBase`` instead of
``declarative_base()``. Includes two helpers that every model inherits:

  * ``to_dict(exclude=...)`` — column-name → value mapping; useful for
    serializing to JSON / caching.
  * ``__repr__`` — sorted ``key=value`` body; useful in shells / logs.

Pattern follows the ``RevlyBase`` mixin from full-stack/data-model-main.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import DeclarativeBase


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

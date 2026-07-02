"""SQLAlchemy mirrors of the technician RBAC grant tables.

Absorbed from agri-api's out-of-band boot script
``back/scripts/ensure_technician_tables.py`` (Django ``apps.irrigation.models``:
``TechnicianGrant`` / ``TechnicianZoneGrant``). The same script also adds the
``CustomUser_customuser.is_technician`` column — that column lives on
``CustomUserCustomuser`` in ``agri.db.users``. Byte-matches the live droplet
schema: all relations are ORM-level in agri-api (Django ``db_constraint=False``)
so there are NO DB-level foreign keys, and no DB defaults.
"""
from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Identity,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from agri.db.base import AgriBase


class AnalyticsTechniciangrant(AgriBase):
    """Links a technician login to the farm owner whose data it may read."""

    __tablename__ = 'analytics_techniciangrant'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='analytics_techniciangrant_pkey'),
        UniqueConstraint('technician_id', 'owner_id', name='uniq_technician_owner'),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1),
        primary_key=True,
    )
    technician_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    owner_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))


class AnalyticsTechnicianzonegrant(AgriBase):
    """Per-zone scope under a grant: which zone + which graph keys are visible.

    ``allowed_graphs`` is a whitelist of ActiveGraph status keys (e.g.
    ``water_flow_status``); effective visibility = granted ∩ owner-enabled.
    """

    __tablename__ = 'analytics_technicianzonegrant'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='analytics_technicianzonegrant_pkey'),
        UniqueConstraint('grant_id', 'zone_id', name='uniq_grant_zone'),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1),
        primary_key=True,
    )
    grant_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    allowed_graphs: Mapped[list] = mapped_column(JSONB, nullable=False)

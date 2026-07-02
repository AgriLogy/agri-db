"""SQLAlchemy mirror of the device registry table (``analytics_device``).

Absorbed from agri-api's out-of-band boot script
``back/scripts/ensure_device_tables.py`` (Django ``apps.irrigation.models.Device``).
Maps a hardware identifier (LoRaWAN DevEUI, Bivocom device_id, serial, ...) to
the owner + zone its readings belong to. Byte-matches the live droplet schema:
``user_id`` / ``zone_id`` are ORM-level relations (Django ``db_constraint=False``)
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
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from agri.db.base import AgriBase


class AnalyticsDevice(AgriBase):
    """A registered hardware router/gateway/node (dragon | lora | bivocom)."""

    __tablename__ = "analytics_device"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="analytics_device_pkey"),
        UniqueConstraint("serial", name="analytics_device_serial_key"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    device_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # dragon|lora|bivocom
    # Hardware identifier: LoRaWAN DevEUI / Bivocom device_id / serial number.
    serial: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    # Last time the owner was emailed about a health issue for this device
    # (device-health beat dedup).
    last_health_notified: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(True)
    )
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

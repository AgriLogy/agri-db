"""Farm-map tables: named sensor installations and per-user map preferences.

Both move state out of agri-web's ``localStorage`` (``agrilogy-farm-sensors-v1``
and the map's camera/basemap) so it survives a cache clear and follows the
farmer across devices (AgriLogy/agri-api#459, Phase 1).

* ``analytics_sensorinstallation`` — a sensor the farmer placed on the map:
  a custom name, a type, a WGS-84 point, the sector it sits in, installation
  details, and (optionally) the reading stream it reports — ``zone_id`` +
  ``sensor_key`` — so the map can show its latest value. ``device_id`` is an
  optional soft link to a registered ``analytics_device``.
* ``analytics_mappreference`` — one row per user: basemap, layer visibility /
  opacity, and the last camera position.
"""

from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    Double,
    ForeignKeyConstraint,
    Identity,
    Index,
    PrimaryKeyConstraint,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from agri.db.base import AgriBase

__all__ = ["AnalyticsMappreference", "AnalyticsSensorinstallation"]


class AnalyticsSensorinstallation(AgriBase):
    """A named sensor placed on the farm map.

    ``sector_id`` / ``zone_id`` are nullable and ``ON DELETE SET NULL``:
    deleting a sector or zone must not silently delete the physical sensor's
    record. ``client_ref`` is the id the browser used before this table
    existed; it makes the one-time localStorage import idempotent.
    """

    __tablename__ = "analytics_sensorinstallation"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            ondelete="CASCADE",
            name="analytics_sensorinstallation_user_id_fk",
        ),
        ForeignKeyConstraint(
            ["sector_id"],
            ["analytics_sector.id"],
            ondelete="SET NULL",
            name="analytics_sensorinstallation_sector_id_fk",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            ondelete="SET NULL",
            name="analytics_sensorinstallation_zone_id_fk",
        ),
        PrimaryKeyConstraint("id", name="analytics_sensorinstallation_pkey"),
        Index("analytics_sensorinstallation_user_id", "user_id"),
        Index(
            "analytics_sensorinstallation_user_client_ref",
            "user_id",
            "client_ref",
            unique=True,
            postgresql_where=text("client_ref IS NOT NULL"),
        ),
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
    sector_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    zone_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    # Soft link to analytics_device (that table has no FKs of its own).
    device_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # Map sensor type (agri-web SENSOR_TYPES id: soil_moisture, flow_meter, ...).
    sensor_type: Mapped[str] = mapped_column(String(40), nullable=False)
    # Reading stream this sensor reports (agri.core SENSOR_KEY_REGISTRY key).
    sensor_key: Mapped[Optional[str]] = mapped_column(String(64))
    latitude: Mapped[float] = mapped_column(Double(53), nullable=False)
    longitude: Mapped[float] = mapped_column(Double(53), nullable=False)
    installation_depth_cm: Mapped[Optional[float]] = mapped_column(Double(53))
    model: Mapped[Optional[str]] = mapped_column(String(100))
    serial_number: Mapped[Optional[str]] = mapped_column(String(128))
    node_id: Mapped[Optional[str]] = mapped_column(String(128))
    installation_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    calibration_profile: Mapped[Optional[str]] = mapped_column(String(100))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    maintenance_status: Mapped[Optional[str]] = mapped_column(String(20))
    client_ref: Mapped[Optional[str]] = mapped_column(String(64))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False, server_default=text("now()")
    )


class AnalyticsMappreference(AgriBase):
    """Per-user farm-map display preferences (one row per user)."""

    __tablename__ = "analytics_mappreference"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            ondelete="CASCADE",
            name="analytics_mappreference_user_id_fk",
        ),
        PrimaryKeyConstraint("user_id", name="analytics_mappreference_pkey"),
    )

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    basemap: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default=text("'satellite_labels'")
    )
    # {"<layer id>": {"visible": bool, "opacity": 0..1}}
    layers: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    # {"center": [lon, lat], "zoom": float, "bearing": float, "pitch": float}
    camera: Mapped[Optional[dict]] = mapped_column(JSONB)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False, server_default=text("now()")
    )

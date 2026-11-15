"""Water level monitoring (AgriLogy/agrilogy-front#261).

Every well, basin or tank on a farm is one ``water_source``. A reading is
always stored in the standard ``WaterLevelReading`` form — water height above
the bottom in metres (``level_m``) — whatever produced it: the in-app
simulator today, a Dragino RS485-LB + level transmitter later. Everything
sensor-specific (DevEUI, Modbus register map, scale/offset) lives on
``water_level_device`` so the calculations and the UI only ever see
``level_m`` plus the source metadata.

* ``water_source``          — geometry, minimum reserve, alert thresholds and
                              the data-source mode (SIMULATED / LIVE /
                              CALIBRATING). All values SI: m, m³.
* ``water_level_device``    — the device feeding a source and its (optional,
                              hardware-dependent) integration settings. Kept
                              configurable: nothing Modbus is hard-coded.
* ``water_level_reading``   — normalised time series, one row per reading.
* ``water_level_alert``     — LOW / CRITICAL / HIGH / OFFLINE events; at most
                              one open (``resolved_at IS NULL``) per source and
                              kind, enforced by a partial unique index.

Like the rest of the schema, ``user_id`` / ``water_source_id`` carry no
DB-level foreign key: the app layer enforces ownership and deletes a source's
devices, readings and alerts with it.
"""

from __future__ import annotations

import datetime
from typing import Any, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Double,
    Identity,
    Index,
    Integer,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from agri.db.base import AgriBase

WATER_SOURCE_TYPES = ("BASIN", "TANK", "WELL")
WATER_SOURCE_GEOMETRIES = ("RECTANGULAR", "CYLINDRICAL", "IRREGULAR")
WATER_SOURCE_MODES = ("SIMULATED", "LIVE", "CALIBRATING")
WATER_READING_MODES = ("SIMULATED", "LIVE")
WATER_READING_QUALITIES = ("GOOD", "SUSPECT", "INVALID")
WATER_ALERT_KINDS = ("LOW", "CRITICAL", "HIGH", "OFFLINE")


def _identity() -> Identity:
    return Identity(
        start=1,
        increment=1,
        minvalue=1,
        maxvalue=9223372036854775807,
        cycle=False,
        cache=1,
    )


def _in(column: str, values: tuple[str, ...]) -> str:
    return f"{column} IN ({', '.join(repr(v) for v in values)})"


class WaterSource(AgriBase):
    """One well, basin or tank and how to turn a level into a volume."""

    __tablename__ = "water_source"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="water_source_pkey"),
        CheckConstraint(
            _in("source_type", WATER_SOURCE_TYPES),
            name="water_source_source_type_check",
        ),
        CheckConstraint(
            _in("geometry", WATER_SOURCE_GEOMETRIES),
            name="water_source_geometry_check",
        ),
        CheckConstraint(
            _in("mode", WATER_SOURCE_MODES), name="water_source_mode_check"
        ),
        CheckConstraint("max_height_m > 0", name="water_source_max_height_check"),
        Index("water_source_user_idx", "user_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, _identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    source_type: Mapped[str] = mapped_column(String(16), nullable=False)
    geometry: Mapped[str] = mapped_column(String(16), nullable=False)
    # Zones this source supplies, as a JSON list of zone ids (display only;
    # no FK, like elsewhere).
    zone_ids: Mapped[list[int]] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    # Highest water column the source can hold, bottom to max-water line.
    max_height_m: Mapped[float] = mapped_column(Double(53), nullable=False)
    length_m: Mapped[Optional[float]] = mapped_column(Double(53), nullable=True)
    width_m: Mapped[Optional[float]] = mapped_column(Double(53), nullable=True)
    diameter_m: Mapped[Optional[float]] = mapped_column(Double(53), nullable=True)
    # Wells: ground level to the bottom, so depth-to-water can be shown.
    total_depth_m: Mapped[Optional[float]] = mapped_column(Double(53), nullable=True)
    # Irregular shapes: declared capacity + [{level_m, volume_m3}, ...].
    max_capacity_m3: Mapped[Optional[float]] = mapped_column(Double(53), nullable=True)
    calibration_table: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(
        JSONB, nullable=True
    )
    minimum_reserve_m3: Mapped[float] = mapped_column(
        Double(53), nullable=False, server_default=text("0")
    )
    low_warning_pct: Mapped[float] = mapped_column(
        Double(53), nullable=False, server_default=text("30")
    )
    critical_pct: Mapped[float] = mapped_column(
        Double(53), nullable=False, server_default=text("15")
    )
    high_pct: Mapped[float] = mapped_column(
        Double(53), nullable=False, server_default=text("95")
    )
    offline_after_min: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("120")
    )
    mode: Mapped[str] = mapped_column(
        String(16), nullable=False, server_default=text("'SIMULATED'")
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )


class WaterLevelDevice(AgriBase):
    """The device feeding a source, with its hardware integration settings."""

    __tablename__ = "water_level_device"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="water_level_device_pkey"),
        UniqueConstraint("device_id", name="water_level_device_device_id_key"),
        Index("water_level_device_source_idx", "water_source_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, _identity(), primary_key=True)
    water_source_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # Stable reading-side identifier, e.g. "simulator_12" or a DevEUI.
    device_id: Mapped[str] = mapped_column(String(64), nullable=False)
    # Which agri-core adapter normalises its payloads ("simulator", ...).
    adapter: Mapped[str] = mapped_column(String(32), nullable=False)
    enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    # raw → level_m: level_m = clamp(raw * scale + offset, 0, max_height_m).
    scale: Mapped[float] = mapped_column(
        Double(53), nullable=False, server_default=text("1")
    )
    offset_m: Mapped[float] = mapped_column(
        Double(53), nullable=False, server_default=text("0")
    )
    # Integration fields, prepared now, filled once the sensor is chosen.
    dev_eui: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    modbus_slave_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    register_address: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    register_type: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    baud_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    parity: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    byte_order: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )


class WaterLevelReading(AgriBase):
    """One normalised level reading (the standard WaterLevelReading)."""

    __tablename__ = "water_level_reading"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="water_level_reading_pkey"),
        CheckConstraint(
            _in("mode", WATER_READING_MODES), name="water_level_reading_mode_check"
        ),
        CheckConstraint(
            _in("quality", WATER_READING_QUALITIES),
            name="water_level_reading_quality_check",
        ),
        Index(
            "water_level_reading_source_measured_idx",
            "water_source_id",
            "measured_at",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, _identity(), primary_key=True)
    water_source_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    device_id: Mapped[str] = mapped_column(String(64), nullable=False)
    mode: Mapped[str] = mapped_column(String(16), nullable=False)
    measured_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )
    received_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )
    level_m: Mapped[float] = mapped_column(Double(53), nullable=False)
    quality: Mapped[str] = mapped_column(
        String(16), nullable=False, server_default=text("'GOOD'")
    )
    battery_percent: Mapped[Optional[float]] = mapped_column(Double(53), nullable=True)
    rssi: Mapped[Optional[float]] = mapped_column(Double(53), nullable=True)
    raw_payload: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)


class WaterLevelAlert(AgriBase):
    """A LOW / CRITICAL / HIGH / OFFLINE event on a water source."""

    __tablename__ = "water_level_alert"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="water_level_alert_pkey"),
        CheckConstraint(
            _in("kind", WATER_ALERT_KINDS), name="water_level_alert_kind_check"
        ),
        Index("water_level_alert_source_idx", "water_source_id", "opened_at"),
        Index(
            "water_level_alert_one_open_idx",
            "water_source_id",
            "kind",
            unique=True,
            postgresql_where=text("resolved_at IS NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, _identity(), primary_key=True)
    water_source_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    opened_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    resolved_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(True), nullable=True
    )
    level_m: Mapped[Optional[float]] = mapped_column(Double(53), nullable=True)
    fill_percent: Mapped[Optional[float]] = mapped_column(Double(53), nullable=True)


__all__ = [
    "WATER_ALERT_KINDS",
    "WATER_READING_MODES",
    "WATER_READING_QUALITIES",
    "WATER_SOURCE_GEOMETRIES",
    "WATER_SOURCE_MODES",
    "WATER_SOURCE_TYPES",
    "WaterLevelAlert",
    "WaterLevelDevice",
    "WaterLevelReading",
    "WaterSource",
]

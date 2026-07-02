"""SQLAlchemy mirrors of the irrigation-automation tables.

Absorbed from agri-api's out-of-band boot script
``back/scripts/ensure_irrigation_tables.py`` (Django ``apps.irrigation.models``:
``IrrigationProgram`` / ``OutputCommand``). Byte-matches the live droplet
schema: all relations are ORM-level in agri-api (Django ``db_constraint=False``)
so there are NO DB-level foreign keys, and no DB defaults.
"""
from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Double,
    Identity,
    Integer,
    PrimaryKeyConstraint,
    String,
    Time,
)
from sqlalchemy.orm import Mapped, mapped_column

from agri.db.base import AgriBase


class AnalyticsIrrigationprogram(AgriBase):
    """A scheduled irrigation program for a zone: fire on the chosen weekdays
    at a start time, for a duration (or target volume). agri-api's beat task
    ``run_due_irrigation_programs`` turns due programs into output commands."""

    __tablename__ = 'analytics_irrigationprogram'
    __table_args__ = (
        CheckConstraint(
            'duration_min >= 0',
            name='analytics_irrigationprogram_duration_min_check',
        ),
        PrimaryKeyConstraint('id', name='analytics_irrigationprogram_pkey'),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    start_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    # Comma-separated ISO weekday numbers (1=Mon ... 7=Sun), e.g. "1,3,5".
    # Empty = every day.
    weekdays: Mapped[str] = mapped_column(String(32), nullable=False)
    duration_min: Mapped[Optional[int]] = mapped_column(Integer)
    target_volume_m3: Mapped[Optional[float]] = mapped_column(Double(53))
    # Last window this program fired in (scheduler dedup).
    last_run_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))


class AnalyticsOutputcommand(AgriBase):
    """A command to an output device (valve/pump) for a zone, created manually
    or by the scheduler. status: pending|simulated|sent|failed."""

    __tablename__ = 'analytics_outputcommand'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='analytics_outputcommand_pkey'),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    device_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    action: Mapped[str] = mapped_column(String(8), nullable=False)  # open|close
    source: Mapped[str] = mapped_column(String(12), nullable=False)  # manual|scheduled
    status: Mapped[str] = mapped_column(String(12), nullable=False)  # pending|simulated|sent|failed
    detail: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    dispatched_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

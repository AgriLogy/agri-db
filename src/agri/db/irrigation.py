"""SQLAlchemy mirrors of the irrigation-automation tables.

``AnalyticsIrrigationprogram`` / ``AnalyticsOutputcommand`` were absorbed from
agri-api's out-of-band boot script ``back/scripts/ensure_irrigation_tables.py``
(Django ``apps.irrigation.models``). They byte-match the live droplet schema:
all their relations are ORM-level in agri-api (Django ``db_constraint=False``)
so there are NO DB-level foreign keys, and no DB defaults.

``AnalyticsIrrigationdecision`` is new to this repo (not a Django mirror), so it
follows the modern convention used by ``analytics_sector`` / ``feedback_bugreport``:
real deferrable foreign keys and DB defaults.
"""

from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Double,
    ForeignKeyConstraint,
    Identity,
    Index,
    Integer,
    PrimaryKeyConstraint,
    String,
    Text,
    Time,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from agri.db.base import AgriBase


class AnalyticsIrrigationprogram(AgriBase):
    """A scheduled irrigation program for a zone: fire on the chosen weekdays
    at a start time, for a duration (or target volume). agri-api's beat task
    ``run_due_irrigation_programs`` turns due programs into output commands."""

    __tablename__ = "analytics_irrigationprogram"
    __table_args__ = (
        CheckConstraint(
            "duration_min >= 0",
            name="analytics_irrigationprogram_duration_min_check",
        ),
        PrimaryKeyConstraint("id", name="analytics_irrigationprogram_pkey"),
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

    __tablename__ = "analytics_outputcommand"
    __table_args__ = (PrimaryKeyConstraint("id", name="analytics_outputcommand_pkey"),)

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
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    device_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    action: Mapped[str] = mapped_column(String(8), nullable=False)  # open|close
    source: Mapped[str] = mapped_column(String(12), nullable=False)  # manual|scheduled
    status: Mapped[str] = mapped_column(
        String(12), nullable=False
    )  # pending|simulated|sent|failed
    detail: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    dispatched_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))


class AnalyticsIrrigationdecision(AgriBase):
    """One row per computed irrigation recommendation — the history behind the
    irrigation report (RPT-1).

    ``agri.core.agronomy.irrigation_decision_dr`` (doc § 4.1-4.2) runs on every
    daily notification / dashboard call and its result is thrown away once the
    email is rendered. This table persists it: the OUTCOME columns are exactly
    the fields of the ``IrrigationDecision`` dataclass, and the INPUT columns are
    exactly the arguments it was called with (plus the ET₀/Kc pair the caller
    derived them from), so a stored row can be re-explained — or recomputed —
    without guessing.

    Reports slice by date range and by zone; see the composite indexes below.
    """

    __tablename__ = "analytics_irrigationdecision"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_irrigationdecision_user_id_fkey",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            ondelete="CASCADE",
            deferrable=True,
            initially="DEFERRED",
            name="analytics_irrigationdecision_zone_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="analytics_irrigationdecision_pkey"),
        Index("analytics_irrigationdecision_zone_decided_idx", "zone_id", "decided_at"),
        Index("analytics_irrigationdecision_user_decided_idx", "user_id", "decided_at"),
        Index("analytics_irrigationdecision_decided_at_idx", "decided_at"),
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
    # When the decision was computed — THE report axis.
    decided_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False, server_default=text("now()")
    )
    # Agronomic day the decision covers (``FieldInputs.date_today``, local tz).
    # Kept alongside ``decided_at`` because the water balance is a daily figure
    # while the computation may run at any hour.
    decision_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # A decision is meaningless without its zone, hence NOT NULL + CASCADE:
    # deleting a zone takes its decision history with it.
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # What produced the row: notification | dashboard | api | scheduler.
    source: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("''")
    )

    # --- Outcome: the IrrigationDecision struct -----------------------------
    irrigate: Mapped[bool] = mapped_column(Boolean, nullable=False)
    # stress | soil_moisture_low | no_stress | rain_will_suffice | complementary
    reason: Mapped[str] = mapped_column(String(32), nullable=False)
    net_mm: Mapped[float] = mapped_column(
        Double(53), nullable=False, server_default=text("0")
    )
    gross_mm: Mapped[float] = mapped_column(
        Double(53), nullable=False, server_default=text("0")
    )
    volume_m3: Mapped[float] = mapped_column(
        Double(53), nullable=False, server_default=text("0")
    )
    duration_hr: Mapped[float] = mapped_column(
        Double(53), nullable=False, server_default=text("0")
    )
    # Set only when duration exceeded the split threshold.
    morning_volume_m3: Mapped[Optional[float]] = mapped_column(Double(53))
    evening_volume_m3: Mapped[Optional[float]] = mapped_column(Double(53))
    capped_to_daily_max: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    # The rendered one-line recommendation shown to the farmer
    # (``agri.core.agronomy._format_decision``), stored verbatim.
    summary: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("''")
    )

    # --- Inputs the decision was computed from ------------------------------
    # Water balance (doc § 4.1). NULL when the zone lacks soil parameters and
    # the decision could not be computed from Dr.
    dr_today_mm: Mapped[Optional[float]] = mapped_column(Double(53))
    raw_mm: Mapped[Optional[float]] = mapped_column(Double(53))
    taw_mm: Mapped[Optional[float]] = mapped_column(Double(53))
    # Evapotranspiration: ET₀ cumulated over the day, the Kc applied, ETc.
    et0_mm: Mapped[Optional[float]] = mapped_column(Double(53))
    kc_used: Mapped[Optional[float]] = mapped_column(Double(53))
    etc_mm: Mapped[Optional[float]] = mapped_column(Double(53))
    # Soil-moisture branch of the trigger logic.
    soil_moisture_pct: Mapped[Optional[float]] = mapped_column(Double(53))
    critical_moisture_pct: Mapped[Optional[float]] = mapped_column(Double(53))
    # Rain branch: forecast and the effective (Pe) part of it.
    precipitation_forecast_mm: Mapped[float] = mapped_column(
        Double(53), nullable=False, server_default=text("0")
    )
    effective_rainfall_mm: Mapped[Optional[float]] = mapped_column(Double(53))
    # Zone/equipment parameters that turned the net depth into m³ and hours.
    zone_area_m2: Mapped[Optional[float]] = mapped_column(Double(53))
    flow_rate_m3h: Mapped[Optional[float]] = mapped_column(Double(53))
    max_water_per_day_m3: Mapped[Optional[float]] = mapped_column(Double(53))
    irrigation_efficiency: Mapped[Optional[float]] = mapped_column(Double(53))
    kr: Mapped[Optional[float]] = mapped_column(Double(53))
    # Anything else worth reporting later without a schema change.
    context: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False, server_default=text("now()")
    )

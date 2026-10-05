"""SQLAlchemy mirrors of every analytics_* table from the live Supabase schema.

47 tables covering: zones/locations, agronomy (ET0, Kc), all sensor reading
tables (air/soil/water/leaf/fruit/energy), alerts/notifications, UI/chart prefs.

Generated from live Supabase dev via sqlacodegen, adapted to use AgriBase
and SQLAlchemy 2.0 idioms.

Phase 4c of the senior-dev refactor.
"""

from __future__ import annotations

import datetime
import decimal
from typing import (
    TYPE_CHECKING,
    Optional,
)  # sqlacodegen-style; clean up to `X | None` in a ratchet

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Double,
    ForeignKeyConstraint,
    Identity,
    Index,
    Integer,
    Numeric,
    PrimaryKeyConstraint,
    String,
    Text,
    Time,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agri.db.base import AgriBase, HasDeviceId

if TYPE_CHECKING:
    # Forward-ref target for the user-side relationships/annotations below.
    # Cross-module string refs resolve via the shared AgriBase registry at
    # runtime; this import only satisfies static analysis (no runtime cycle).
    from agri.db.users import CustomUserCustomuser


class AnalyticsKcperiod(AgriBase):
    __tablename__ = "analytics_kcperiod"
    __table_args__ = (PrimaryKeyConstraint("id", name="analytics_kcperiod_pkey"),)

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
    period_name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    end_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    kc_value: Mapped[float] = mapped_column(Double(53), nullable=False)

    analytics_kcperiodassignment: Mapped[list["AnalyticsKcperiodassignment"]] = (
        relationship("AnalyticsKcperiodassignment", back_populates="period")
    )


class AnalyticsManageraffirmation(AgriBase):
    __tablename__ = "analytics_manageraffirmation"
    __table_args__ = (
        ForeignKeyConstraint(
            ["decided_by_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_manageraff_decided_by_id_f802a23b_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["requested_by_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_manageraff_requested_by_id_707f0882_fk_CustomUse",
        ),
        PrimaryKeyConstraint("id", name="analytics_manageraffirmation_pkey"),
        Index("analytics_m_request_3d1a18_idx", "requested_by_id"),
        Index("analytics_m_status_6a59c1_idx", "status"),
        Index("analytics_manageraffirmation_decided_by_id_f802a23b", "decided_by_id"),
        Index(
            "analytics_manageraffirmation_requested_by_id_707f0882", "requested_by_id"
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
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    decision_note: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )
    requested_by_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    decided_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    decided_by_id: Mapped[Optional[int]] = mapped_column(BigInteger)

    decided_by: Mapped[Optional["CustomUserCustomuser"]] = relationship(
        "CustomUserCustomuser",
        foreign_keys=[decided_by_id],
        back_populates="analytics_manageraffirmation_decided_by",
    )
    requested_by: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser",
        foreign_keys=[requested_by_id],
        back_populates="analytics_manageraffirmation_requested_by",
    )


class AnalyticsNotification(AgriBase):
    __tablename__ = "analytics_notification"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_notificati_user_id_ac921281_fk_CustomUse",
        ),
        PrimaryKeyConstraint("id", name="analytics_notification_pkey"),
        Index("analytics_notification_user_id_ac921281", "user_id"),
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
    yesterday_temperature: Mapped[decimal.Decimal] = mapped_column(
        Numeric(5, 2), nullable=False
    )
    today_temperature: Mapped[decimal.Decimal] = mapped_column(
        Numeric(5, 2), nullable=False
    )
    yesterday_humidity: Mapped[decimal.Decimal] = mapped_column(
        Numeric(5, 2), nullable=False
    )
    today_humidity: Mapped[decimal.Decimal] = mapped_column(
        Numeric(5, 2), nullable=False
    )
    ET0: Mapped[decimal.Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    soil_humidity: Mapped[decimal.Decimal] = mapped_column(
        Numeric(5, 2), nullable=False
    )
    soil_temperature: Mapped[decimal.Decimal] = mapped_column(
        Numeric(5, 2), nullable=False
    )
    soil_ph: Mapped[decimal.Decimal] = mapped_column(Numeric(4, 2), nullable=False)
    perfect_irrigation_period: Mapped[str] = mapped_column(String(100), nullable=False)
    last_irrigation_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    last_start_irrigation_hour: Mapped[datetime.time] = mapped_column(
        Time, nullable=False
    )
    last_finish_irrigation_hour: Mapped[datetime.time] = mapped_column(
        Time, nullable=False
    )
    used_water_irrigation: Mapped[decimal.Decimal] = mapped_column(
        Numeric(7, 2), nullable=False
    )
    notification_date: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger)

    user: Mapped[Optional["CustomUserCustomuser"]] = relationship(
        "CustomUserCustomuser", back_populates="analytics_notification"
    )


class AnalyticsUsersensorunitpreference(AgriBase):
    __tablename__ = "analytics_usersensorunitpreference"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_usersensor_user_id_78477443_fk_CustomUse",
        ),
        PrimaryKeyConstraint("id", name="analytics_usersensorunitpreference_pkey"),
        UniqueConstraint(
            "user_id",
            "sensor_key",
            name="analytics_usersensorunit_user_id_sensor_key_edd02596_uniq",
        ),
        Index("analytics_u_user_id_9051b6_idx", "user_id", "sensor_key"),
        Index("analytics_usersensorunitpreference_user_id_78477443", "user_id"),
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
    sensor_key: Mapped[str] = mapped_column(String(64), nullable=False)
    unit: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_usersensorunitpreference"
    )


class AnalyticsSector(AgriBase):
    """Organizational grouping of zones under a user's farm: User → Sector →
    Zone. Zones reference it via ``analytics_zone.sector_id`` (nullable =
    unassigned). Deleting a sector only unassigns its zones (ON DELETE SET
    NULL), never deletes them.

    Optionally carries the sector's drawn shape (``geometry``, GeoJSON in
    JSONB) with its derived ``area_ha`` / ``perimeter_m`` and map ``color``.
    All are nullable: a name-only sector that has never been drawn predates
    the map and stays valid. ``area_ha`` / ``perimeter_m`` are written by the
    API from ``geometry`` and are never client-supplied."""

    __tablename__ = "analytics_sector"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_sector_user_id_fk_CustomUser_customuser_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_sector_pkey"),
        Index("analytics_sector_user_id", "user_id"),
        Index(
            "analytics_sector_user_id_drawn",
            "user_id",
            postgresql_where=text("geometry IS NOT NULL"),
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
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    geometry: Mapped[Optional[dict]] = mapped_column(JSONB)
    area_ha: Mapped[Optional[float]] = mapped_column(Double(53))
    perimeter_m: Mapped[Optional[float]] = mapped_column(Double(53))
    color: Mapped[Optional[str]] = mapped_column(String(9))
    geometry_updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(True)
    )

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_sector"
    )
    zones: Mapped[list["AnalyticsZone"]] = relationship(
        "AnalyticsZone", back_populates="sector"
    )


class AnalyticsZone(AgriBase):
    __tablename__ = "analytics_zone"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_zone_user_id_b7a7ebd7_fk_CustomUser_customuser_id",
        ),
        ForeignKeyConstraint(
            ["sector_id"],
            ["analytics_sector.id"],
            deferrable=True,
            initially="DEFERRED",
            ondelete="SET NULL",
            name="analytics_zone_sector_id_fk_analytics_sector_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_zone_pkey"),
        Index("analytics_zone_user_id_b7a7ebd7", "user_id"),
        Index("analytics_zone_sector_id", "sector_id"),
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
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    space: Mapped[float] = mapped_column(Double(53), nullable=False)
    critical_moisture_threshold: Mapped[float] = mapped_column(
        Double(53), nullable=False
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    irrigation_water_quantity: Mapped[float] = mapped_column(Double(53), nullable=False)
    pomp_flow_rate: Mapped[float] = mapped_column(Double(53), nullable=False)
    soil_param_FC: Mapped[float] = mapped_column(Double(53), nullable=False)
    soil_param_RAW: Mapped[float] = mapped_column(Double(53), nullable=False)
    soil_param_TAW: Mapped[float] = mapped_column(Double(53), nullable=False)
    soil_param_WP: Mapped[float] = mapped_column(Double(53), nullable=False)
    elevation_m: Mapped[float] = mapped_column(
        Double(53), nullable=False, server_default=text("0")
    )
    # Basin / reservoir geometry (ultrasonic level sensor). Nullable: only
    # set for zones with a level sensor. Legacy trio restored from dropped
    # e8a1c7f4d2b9; rectangle trio is new (L x W x H_tot).
    basin_max_depth_m: Mapped[Optional[float]] = mapped_column(
        Double(53), nullable=True
    )
    basin_area_m2: Mapped[Optional[float]] = mapped_column(
        Double(53), nullable=True
    )
    sensor_mount_offset_m: Mapped[Optional[float]] = mapped_column(
        Double(53), nullable=True
    )
    basin_length_m: Mapped[Optional[float]] = mapped_column(
        Double(53), nullable=True
    )
    basin_width_m: Mapped[Optional[float]] = mapped_column(
        Double(53), nullable=True
    )
    basin_height_m: Mapped[Optional[float]] = mapped_column(
        Double(53), nullable=True
    )
    # User → Sector → Zone grouping. Nullable: a zone with no sector is
    # "unassigned" (backfill leaves every existing zone here).
    sector_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_zone"
    )
    sector: Mapped[Optional["AnalyticsSector"]] = relationship(
        "AnalyticsSector", back_populates="zones"
    )
    analytics_activegraph: Mapped[list["AnalyticsActivegraph"]] = relationship(
        "AnalyticsActivegraph", back_populates="zone"
    )
    analytics_alert: Mapped[list["AnalyticsAlert"]] = relationship(
        "AnalyticsAlert", back_populates="zone"
    )
    analytics_ecsalinitysensor: Mapped[list["AnalyticsEcsalinitysensor"]] = (
        relationship("AnalyticsEcsalinitysensor", back_populates="zone")
    )
    analytics_ecsoilhigh: Mapped[list["AnalyticsEcsoilhigh"]] = relationship(
        "AnalyticsEcsoilhigh", back_populates="zone"
    )
    analytics_ecsoillow: Mapped[list["AnalyticsEcsoillow"]] = relationship(
        "AnalyticsEcsoillow", back_populates="zone"
    )
    analytics_ecsoilmedium: Mapped[list["AnalyticsEcsoilmedium"]] = relationship(
        "AnalyticsEcsoilmedium", back_populates="zone"
    )
    analytics_electricityconsumptionsensor: Mapped[
        list["AnalyticsElectricityconsumptionsensor"]
    ] = relationship("AnalyticsElectricityconsumptionsensor", back_populates="zone")
    analytics_et0calculated: Mapped[list["AnalyticsEt0calculated"]] = relationship(
        "AnalyticsEt0calculated", back_populates="zone"
    )
    analytics_et0weather: Mapped[list["AnalyticsEt0weather"]] = relationship(
        "AnalyticsEt0weather", back_populates="zone"
    )
    analytics_fruitsizesensor: Mapped[list["AnalyticsFruitsizesensor"]] = relationship(
        "AnalyticsFruitsizesensor", back_populates="zone"
    )
    analytics_graphname: Mapped[list["AnalyticsGraphname"]] = relationship(
        "AnalyticsGraphname", back_populates="zone"
    )
    analytics_humidityweather: Mapped[list["AnalyticsHumidityweather"]] = relationship(
        "AnalyticsHumidityweather", back_populates="zone"
    )
    analytics_kc: Mapped[list["AnalyticsKc"]] = relationship(
        "AnalyticsKc", back_populates="zone"
    )
    analytics_largefruitdiametersensor: Mapped[
        list["AnalyticsLargefruitdiametersensor"]
    ] = relationship("AnalyticsLargefruitdiametersensor", back_populates="zone")
    analytics_leafmoisturesensor: Mapped[list["AnalyticsLeafmoisturesensor"]] = (
        relationship("AnalyticsLeafmoisturesensor", back_populates="zone")
    )
    analytics_leaftemperaturesensor: Mapped[list["AnalyticsLeaftemperaturesensor"]] = (
        relationship("AnalyticsLeaftemperaturesensor", back_populates="zone")
    )
    analytics_multidepthsoilmoisturesensor: Mapped[
        list["AnalyticsMultidepthsoilmoisturesensor"]
    ] = relationship("AnalyticsMultidepthsoilmoisturesensor", back_populates="zone")
    analytics_npksensor: Mapped[list["AnalyticsNpksensor"]] = relationship(
        "AnalyticsNpksensor", back_populates="zone"
    )
    analytics_phsoil: Mapped[list["AnalyticsPhsoil"]] = relationship(
        "AnalyticsPhsoil", back_populates="zone"
    )
    analytics_phwatersensor: Mapped[list["AnalyticsPhwatersensor"]] = relationship(
        "AnalyticsPhwatersensor", back_populates="zone"
    )
    analytics_precipitationrate: Mapped[list["AnalyticsPrecipitationrate"]] = (
        relationship("AnalyticsPrecipitationrate", back_populates="zone")
    )
    analytics_pressureweather: Mapped[list["AnalyticsPressureweather"]] = relationship(
        "AnalyticsPressureweather", back_populates="zone"
    )
    analytics_sensorcolor: Mapped[list["AnalyticsSensorcolor"]] = relationship(
        "AnalyticsSensorcolor", back_populates="zone"
    )
    analytics_sensorlocation: Mapped[list["AnalyticsSensorlocation"]] = relationship(
        "AnalyticsSensorlocation", back_populates="zone"
    )
    analytics_soilconductivitysensor: Mapped[
        list["AnalyticsSoilconductivitysensor"]
    ] = relationship("AnalyticsSoilconductivitysensor", back_populates="zone")
    analytics_soilmoisturehigh: Mapped[list["AnalyticsSoilmoisturehigh"]] = (
        relationship("AnalyticsSoilmoisturehigh", back_populates="zone")
    )
    analytics_soilmoisturelow: Mapped[list["AnalyticsSoilmoisturelow"]] = relationship(
        "AnalyticsSoilmoisturelow", back_populates="zone"
    )
    analytics_soilmoisturemedium: Mapped[list["AnalyticsSoilmoisturemedium"]] = (
        relationship("AnalyticsSoilmoisturemedium", back_populates="zone")
    )
    analytics_soilsalinitysensor: Mapped[list["AnalyticsSoilsalinitysensor"]] = (
        relationship("AnalyticsSoilsalinitysensor", back_populates="zone")
    )
    analytics_soiltemperaturehigh: Mapped[list["AnalyticsSoiltemperaturehigh"]] = (
        relationship("AnalyticsSoiltemperaturehigh", back_populates="zone")
    )
    analytics_soiltemperaturelow: Mapped[list["AnalyticsSoiltemperaturelow"]] = (
        relationship("AnalyticsSoiltemperaturelow", back_populates="zone")
    )
    analytics_soiltemperaturemedium: Mapped[list["AnalyticsSoiltemperaturemedium"]] = (
        relationship("AnalyticsSoiltemperaturemedium", back_populates="zone")
    )
    analytics_solarradiation: Mapped[list["AnalyticsSolarradiation"]] = relationship(
        "AnalyticsSolarradiation", back_populates="zone"
    )
    analytics_temperatureweather: Mapped[list["AnalyticsTemperatureweather"]] = (
        relationship("AnalyticsTemperatureweather", back_populates="zone")
    )
    analytics_vpdweather: Mapped[list["AnalyticsVpdweather"]] = relationship(
        "AnalyticsVpdweather", back_populates="zone"
    )
    analytics_waterecsensor: Mapped[list["AnalyticsWaterecsensor"]] = relationship(
        "AnalyticsWaterecsensor", back_populates="zone"
    )
    analytics_waterflowsensor: Mapped[list["AnalyticsWaterflowsensor"]] = relationship(
        "AnalyticsWaterflowsensor", back_populates="zone"
    )
    analytics_waterlevelsensor: Mapped[list["AnalyticsWaterlevelsensor"]] = (
        relationship("AnalyticsWaterlevelsensor", back_populates="zone")
    )
    analytics_waterpressuresensor: Mapped[list["AnalyticsWaterpressuresensor"]] = (
        relationship("AnalyticsWaterpressuresensor", back_populates="zone")
    )
    analytics_winddirection: Mapped[list["AnalyticsWinddirection"]] = relationship(
        "AnalyticsWinddirection", back_populates="zone"
    )
    analytics_windspeed: Mapped[list["AnalyticsWindspeed"]] = relationship(
        "AnalyticsWindspeed", back_populates="zone"
    )


class AnalyticsActivegraph(AgriBase):
    __tablename__ = "analytics_activegraph"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_activegrap_user_id_f47c5422_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_activegraph_zone_id_937afabc_fk_analytics_zone_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_activegraph_pkey"),
        Index("analytics_activegraph_user_id_f47c5422", "user_id"),
        Index("analytics_activegraph_zone_id_937afabc", "zone_id"),
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
    soil_irrigation_status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    soil_ph_status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    soil_conductivity_status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    soil_moisture_status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    soil_temperature_status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    et0_status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    wind_speed_status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    solar_radiation_status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    wind_direction_status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    temperature_humidity_weather_status: Mapped[bool] = mapped_column(
        Boolean, nullable=False
    )
    precipitation_humidity_rate_status: Mapped[bool] = mapped_column(
        Boolean, nullable=False
    )
    data_table_status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    electricity_consumption_status: Mapped[bool] = mapped_column(
        Boolean, nullable=False
    )
    fruit_size_status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    large_fruit_diameter_status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    leaf_sensor_status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    npk_status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    pluviometry_status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    water_ec_status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    water_flow_status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    water_ph_status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    water_pressure_status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    water_level_status: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    cumulative_precipitation_status: Mapped[bool] = mapped_column(
        Boolean, nullable=False
    )
    precipitation_rate_status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    weather_temperature_humidity_status: Mapped[bool] = mapped_column(
        Boolean, nullable=False
    )
    wind_radar_status: Mapped[bool] = mapped_column(Boolean, nullable=False)

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_activegraph"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_activegraph"
    )


class AnalyticsAlert(AgriBase):
    __tablename__ = "analytics_alert"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_alert_user_id_dc15c219_fk_CustomUser_customuser_id",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_alert_zone_id_8b2af397_fk_analytics_zone_id",
        ),
        # Matches the DB exactly: e2f3a4b5c6d7 created this FK inline
        # (auto-named *_fkey) with ON DELETE SET NULL — declaring it any other
        # way makes `alembic check` report drift.
        ForeignKeyConstraint(
            ["notification_zone_id"],
            ["analytics_notificationzone.id"],
            ondelete="SET NULL",
            deferrable=True,
            initially="DEFERRED",
            name="analytics_alert_notification_zone_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="analytics_alert_pkey"),
        Index("analytics_alert_user_id_dc15c219", "user_id"),
        Index("analytics_alert_zone_id_8b2af397", "zone_id"),
        Index("analytics_alert_notification_zone_id_idx", "notification_zone_id"),
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
    description: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    condition: Mapped[str] = mapped_column(String(1), nullable=False)
    condition_nbr: Mapped[decimal.Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    sensor_key: Mapped[str] = mapped_column(String(64), nullable=False)
    notify_email: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    notify_whatsapp: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    notify_sms: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    grace_override_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    last_triggered_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(True)
    )
    last_emailed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    zone_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    notification_zone_id: Mapped[Optional[int]] = mapped_column(BigInteger)

    user: Mapped[Optional["CustomUserCustomuser"]] = relationship(
        "CustomUserCustomuser", back_populates="analytics_alert"
    )
    zone: Mapped[Optional["AnalyticsZone"]] = relationship(
        "AnalyticsZone", back_populates="analytics_alert"
    )
    notification_zone: Mapped[Optional["AnalyticsNotificationzone"]] = relationship(
        "AnalyticsNotificationzone", back_populates="analytics_alert"
    )


class AnalyticsAlertevent(AgriBase):
    """One row per alert *firing* — the history behind the alert report (RPT-1).

    ``analytics_alert`` holds the rule and only ever keeps the LAST trigger
    (``last_triggered_at`` / ``last_emailed_at``), so nothing today can answer
    "what fired in this zone last month". This table is that append-only log:
    the evaluation that ``agri.core.alerts.evaluate_alert`` found true, with the
    observed reading and the threshold it violated captured at the moment of the
    firing.

    Denormalised on purpose: ``alert_name`` / ``condition`` / ``threshold_value``
    / ``unit`` are snapshots, so the report still reads correctly after the rule
    is edited or deleted (``alert_id`` is ON DELETE SET NULL). Reports slice by
    date range and by zone — see the composite indexes below.
    """

    __tablename__ = "analytics_alertevent"
    __table_args__ = (
        ForeignKeyConstraint(
            ["alert_id"],
            ["analytics_alert.id"],
            ondelete="SET NULL",
            deferrable=True,
            initially="DEFERRED",
            name="analytics_alertevent_alert_id_fkey",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_alertevent_user_id_fkey",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            ondelete="SET NULL",
            deferrable=True,
            initially="DEFERRED",
            name="analytics_alertevent_zone_id_fkey",
        ),
        ForeignKeyConstraint(
            ["notification_zone_id"],
            ["analytics_notificationzone.id"],
            ondelete="SET NULL",
            deferrable=True,
            initially="DEFERRED",
            name="analytics_alertevent_notification_zone_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="analytics_alertevent_pkey"),
        # Report query shape: "date range + zone", "date range + user".
        Index("analytics_alertevent_zone_triggered_idx", "zone_id", "triggered_at"),
        Index("analytics_alertevent_user_triggered_idx", "user_id", "triggered_at"),
        Index("analytics_alertevent_triggered_at_idx", "triggered_at"),
        Index("analytics_alertevent_alert_id_idx", "alert_id"),
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
    # When the condition was found true. THE report axis (not created_at).
    triggered_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False, server_default=text("now()")
    )
    # The rule that fired. Nullable + ON DELETE SET NULL so deleting an alert
    # never erases its history.
    alert_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    # Owner — every report is scoped to one account.
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # Farm zone the reading came from. NULL when the alert is user-wide, i.e.
    # ``agri.core.alerts.effective_zone_id_for_alert`` resolved to None.
    zone_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    # Set when the alert is bound to a custom notification zone instead of a
    # farm zone (agrilogy-front #57).
    notification_zone_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    # Soft FK to analytics_device (Django-managed; same convention as
    # ``HasDeviceId`` on the reading tables) — which physical device/sensor
    # produced the offending reading. NULL for weather / user-wide readings.
    device_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    # Reading stream, e.g. "soilmoisturemedium" (agri.core SENSOR_KEY_REGISTRY).
    sensor_key: Mapped[str] = mapped_column(String(64), nullable=False)
    # Snapshots of the rule as it was when it fired.
    alert_name: Mapped[str] = mapped_column(
        String(200), nullable=False, server_default=text("''")
    )
    condition: Mapped[str] = mapped_column(String(1), nullable=False)  # > | < | =
    threshold_value: Mapped[float] = mapped_column(Double(53), nullable=False)
    # The reading that violated the threshold, and when it was recorded
    # (``reading_at`` differs from ``triggered_at``: evaluation is periodic).
    observed_value: Mapped[float] = mapped_column(Double(53), nullable=False)
    reading_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    # Unit label snapshot (registry lookup) so the report needs no join.
    unit: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("''")
    )
    # Comma-separated channels actually notified, e.g. "email,whatsapp".
    # Empty when the firing was recorded but no notification went out.
    notified_channels: Mapped[str] = mapped_column(
        String(64), nullable=False, server_default=text("''")
    )
    # Free-form extra context for the report (sensor label, sector, raw payload).
    context: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False, server_default=text("now()")
    )


class AnalyticsNotificationzone(AgriBase):
    """User-owned alert grouping independent of the farm ``analytics_zone`` rows
    (agrilogy-front #57). Sensors are attached via ``AnalyticsNotificationzonesensor``;
    an ``AnalyticsAlert`` may bind here instead of to a farm zone."""

    __tablename__ = "analytics_notificationzone"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_notificationzone_user_id_fk",
        ),
        PrimaryKeyConstraint("id", name="analytics_notificationzone_pkey"),
        Index("analytics_notificationzone_user_id_idx", "user_id"),
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
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("''")
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    sensors: Mapped[list["AnalyticsNotificationzonesensor"]] = relationship(
        "AnalyticsNotificationzonesensor", back_populates="notification_zone"
    )
    analytics_alert: Mapped[list["AnalyticsAlert"]] = relationship(
        "AnalyticsAlert", back_populates="notification_zone"
    )


class AnalyticsNotificationzonesensor(AgriBase):
    """One sensor stream assigned to a notification zone: ``sensor_key`` read from
    farm zone ``source_zone_id`` (null = the user-wide latest reading)."""

    __tablename__ = "analytics_notificationzonesensor"
    __table_args__ = (
        ForeignKeyConstraint(
            ["notification_zone_id"],
            ["analytics_notificationzone.id"],
            ondelete="CASCADE",
            deferrable=True,
            initially="DEFERRED",
            name="analytics_notificationzonesensor_zone_id_fk",
        ),
        ForeignKeyConstraint(
            ["source_zone_id"],
            ["analytics_zone.id"],
            ondelete="SET NULL",
            deferrable=True,
            initially="DEFERRED",
            name="analytics_notificationzonesensor_source_zone_id_fk",
        ),
        PrimaryKeyConstraint("id", name="analytics_notificationzonesensor_pkey"),
        Index("analytics_notificationzonesensor_zone_idx", "notification_zone_id"),
        Index("analytics_notificationzonesensor_source_idx", "source_zone_id"),
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
    sensor_key: Mapped[str] = mapped_column(String(64), nullable=False)
    label: Mapped[Optional[str]] = mapped_column(String(200))
    notification_zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    source_zone_id: Mapped[Optional[int]] = mapped_column(BigInteger)

    notification_zone: Mapped["AnalyticsNotificationzone"] = relationship(
        "AnalyticsNotificationzone", back_populates="sensors"
    )
    source_zone: Mapped[Optional["AnalyticsZone"]] = relationship("AnalyticsZone")


class AnalyticsDevicesensor(AgriBase):
    """One physical sensor carried by a registered router/gateway. Maps a device's
    wire tag (e.g. a Bivocom Modbus tag like ``ta``) to a ``sensor_key`` and the farm
    zone its readings belong to (null = the device's own zone). Lets an admin onboard
    a router's sensors as DATA — no per-device code. ``device_id`` is a soft FK:
    ``analytics_device`` is a Django-managed table, not mirrored here."""

    __tablename__ = "analytics_devicesensor"
    __table_args__ = (
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            ondelete="SET NULL",
            deferrable=True,
            initially="DEFERRED",
            name="analytics_devicesensor_zone_id_fk",
        ),
        PrimaryKeyConstraint("id", name="analytics_devicesensor_pkey"),
        UniqueConstraint(
            "device_id", "tag_name", name="analytics_devicesensor_device_tag_uniq"
        ),
        Index("analytics_devicesensor_device_idx", "device_id"),
        Index("analytics_devicesensor_zone_idx", "zone_id"),
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
    device_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tag_name: Mapped[str] = mapped_column(String(64), nullable=False)
    sensor_key: Mapped[str] = mapped_column(String(64), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    zone_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    zone: Mapped[Optional["AnalyticsZone"]] = relationship("AnalyticsZone")


class AnalyticsEcsalinitysensor(AgriBase, HasDeviceId):
    __tablename__ = "analytics_ecsalinitysensor"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_ecsalinity_user_id_7863f084_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_ecsalinity_zone_id_bc5b3e88_fk_analytics",
        ),
        PrimaryKeyConstraint("id", name="analytics_ecsalinitysensor_pkey"),
        Index("analytics_ecsalinitysensor_user_id_7863f084", "user_id"),
        Index("analytics_ecsalinitysensor_zone_id_bc5b3e88", "zone_id"),
        Index(
            "ix_analytics_ecsalinitysensor_user_id_timestamp", "user_id", "timestamp"
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_ecsalinitysensor"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_ecsalinitysensor"
    )


class AnalyticsEcsoilhigh(AgriBase, HasDeviceId):
    __tablename__ = "analytics_ecsoilhigh"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_soilechigh_user_id_ba0aeab8_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_soilechigh_zone_id_9b3051a1_fk_analytics_zone_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_soilechigh_pkey"),
        Index("analytics_soilechigh_user_id_ba0aeab8", "user_id"),
        Index("analytics_soilechigh_zone_id_9b3051a1", "zone_id"),
        Index("ix_analytics_ecsoilhigh_user_id_timestamp", "user_id", "timestamp"),
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_ecsoilhigh"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_ecsoilhigh"
    )


class AnalyticsEcsoillow(AgriBase, HasDeviceId):
    __tablename__ = "analytics_ecsoillow"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_ecsoillow_user_id_f1f8b9b1_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_ecsoillow_zone_id_6435968a_fk_analytics_zone_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_ecsoillow_pkey"),
        Index("analytics_ecsoillow_user_id_f1f8b9b1", "user_id"),
        Index("analytics_ecsoillow_zone_id_6435968a", "zone_id"),
        Index("ix_analytics_ecsoillow_user_id_timestamp", "user_id", "timestamp"),
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_ecsoillow"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_ecsoillow"
    )


class AnalyticsEcsoilmedium(AgriBase, HasDeviceId):
    __tablename__ = "analytics_ecsoilmedium"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_ecsoilmedi_user_id_af4e0840_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_ecsoilmedium_zone_id_26b984b6_fk_analytics_zone_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_ecsoilmedium_pkey"),
        Index("analytics_ecsoilmedium_user_id_af4e0840", "user_id"),
        Index("analytics_ecsoilmedium_zone_id_26b984b6", "zone_id"),
        Index("ix_analytics_ecsoilmedium_user_id_timestamp", "user_id", "timestamp"),
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_ecsoilmedium"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_ecsoilmedium"
    )


class AnalyticsElectricityconsumptionsensor(AgriBase, HasDeviceId):
    __tablename__ = "analytics_electricityconsumptionsensor"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_electricit_user_id_03f25332_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_electricit_zone_id_a532e0be_fk_analytics",
        ),
        PrimaryKeyConstraint("id", name="analytics_electricityconsumptionsensor_pkey"),
        Index("analytics_electricityconsumptionsensor_user_id_03f25332", "user_id"),
        Index("analytics_electricityconsumptionsensor_zone_id_a532e0be", "zone_id"),
        Index(
            "ix_analytics_electricityconsumptionsensor_user_id_timestamp",
            "user_id",
            "timestamp",
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_electricityconsumptionsensor"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_electricityconsumptionsensor"
    )


class AnalyticsEt0calculated(AgriBase, HasDeviceId):
    __tablename__ = "analytics_et0calculated"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_et0calcula_user_id_99546ca9_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_et0calculated_zone_id_620e335a_fk_analytics_zone_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_et0calculated_pkey"),
        Index("analytics_et0calculated_user_id_99546ca9", "user_id"),
        Index("analytics_et0calculated_zone_id_620e335a", "zone_id"),
        Index("ix_analytics_et0calculated_user_id_timestamp", "user_id", "timestamp"),
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_et0calculated"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_et0calculated"
    )


class AnalyticsEt0weather(AgriBase, HasDeviceId):
    __tablename__ = "analytics_et0weather"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_et0weather_user_id_f6f47f3f_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_et0weather_zone_id_466ea3ec_fk_analytics_zone_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_et0weather_pkey"),
        Index("analytics_et0weather_user_id_f6f47f3f", "user_id"),
        Index("analytics_et0weather_zone_id_466ea3ec", "zone_id"),
        Index("ix_analytics_et0weather_user_id_timestamp", "user_id", "timestamp"),
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_et0weather"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_et0weather"
    )


class AnalyticsFruitsizesensor(AgriBase, HasDeviceId):
    __tablename__ = "analytics_fruitsizesensor"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_fruitsizes_user_id_3baef23e_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_fruitsizesensor_zone_id_e811413e_fk_analytics_zone_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_fruitsizesensor_pkey"),
        Index("analytics_fruitsizesensor_user_id_3baef23e", "user_id"),
        Index("analytics_fruitsizesensor_zone_id_e811413e", "zone_id"),
        Index("ix_analytics_fruitsizesensor_user_id_timestamp", "user_id", "timestamp"),
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_fruitsizesensor"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_fruitsizesensor"
    )


class AnalyticsGraphname(AgriBase):
    __tablename__ = "analytics_graphname"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_graphname_user_id_981b56d5_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_graphname_zone_id_e9ed11e5_fk_analytics_zone_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_graphname_pkey"),
        Index("analytics_graphname_user_id_981b56d5", "user_id"),
        Index("analytics_graphname_zone_id_e9ed11e5", "zone_id"),
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
    soil_irrigation: Mapped[str] = mapped_column(String(40), nullable=False)
    soil_ph: Mapped[str] = mapped_column(String(40), nullable=False)
    soil_conductivity: Mapped[str] = mapped_column(String(40), nullable=False)
    soil_moisture: Mapped[str] = mapped_column(String(40), nullable=False)
    soil_temperature: Mapped[str] = mapped_column(String(40), nullable=False)
    et0: Mapped[str] = mapped_column(String(40), nullable=False)
    precipitation_rate: Mapped[str] = mapped_column(String(40), nullable=False)
    wind_speed: Mapped[str] = mapped_column(String(40), nullable=False)
    solar_radiation: Mapped[str] = mapped_column(String(40), nullable=False)
    pressure_weather: Mapped[str] = mapped_column(String(40), nullable=False)
    wind_direction: Mapped[str] = mapped_column(String(40), nullable=False)
    humidity_weather: Mapped[str] = mapped_column(String(40), nullable=False)
    temperature_weather: Mapped[str] = mapped_column(String(40), nullable=False)
    temperature_humidity_weather: Mapped[str] = mapped_column(
        String(40), nullable=False
    )
    precipitation_humidity_rate: Mapped[str] = mapped_column(String(40), nullable=False)
    pluviometrie: Mapped[str] = mapped_column(String(40), nullable=False)
    data_table: Mapped[str] = mapped_column(String(40), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[Optional[int]] = mapped_column(BigInteger)

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_graphname"
    )
    zone: Mapped[Optional["AnalyticsZone"]] = relationship(
        "AnalyticsZone", back_populates="analytics_graphname"
    )


class AnalyticsHumidityweather(AgriBase, HasDeviceId):
    __tablename__ = "analytics_humidityweather"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_humiditywe_user_id_27a943ca_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_humidityweather_zone_id_aeee65d6_fk_analytics_zone_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_humidityweather_pkey"),
        Index("analytics_humidityweather_user_id_27a943ca", "user_id"),
        Index("analytics_humidityweather_zone_id_aeee65d6", "zone_id"),
        Index("ix_analytics_humidityweather_user_id_timestamp", "user_id", "timestamp"),
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_humidityweather"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_humidityweather"
    )


class AnalyticsKc(AgriBase):
    __tablename__ = "analytics_kc"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_kc_user_id_e5b99f45_fk_CustomUser_customuser_id",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_kc_zone_id_75af8af5_fk_analytics_zone_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_kc_pkey"),
        Index("analytics_kc_user_id_e5b99f45", "user_id"),
        Index("analytics_kc_zone_id_75af8af5", "zone_id"),
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
    plant_name: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    number_of_periods: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    zone_id: Mapped[Optional[int]] = mapped_column(BigInteger)

    user: Mapped[Optional["CustomUserCustomuser"]] = relationship(
        "CustomUserCustomuser", back_populates="analytics_kc"
    )
    zone: Mapped[Optional["AnalyticsZone"]] = relationship(
        "AnalyticsZone", back_populates="analytics_kc"
    )
    analytics_kcperiodassignment: Mapped[list["AnalyticsKcperiodassignment"]] = (
        relationship("AnalyticsKcperiodassignment", back_populates="kc")
    )


class AnalyticsLargefruitdiametersensor(AgriBase, HasDeviceId):
    __tablename__ = "analytics_largefruitdiametersensor"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_largefruit_user_id_7029b33d_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_largefruit_zone_id_adf5ba65_fk_analytics",
        ),
        PrimaryKeyConstraint("id", name="analytics_largefruitdiametersensor_pkey"),
        Index("analytics_largefruitdiametersensor_user_id_7029b33d", "user_id"),
        Index("analytics_largefruitdiametersensor_zone_id_adf5ba65", "zone_id"),
        Index(
            "ix_analytics_largefruitdiametersensor_user_id_timestamp",
            "user_id",
            "timestamp",
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_largefruitdiametersensor"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_largefruitdiametersensor"
    )


class AnalyticsLeafmoisturesensor(AgriBase, HasDeviceId):
    __tablename__ = "analytics_leafmoisturesensor"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_leafmoistu_user_id_46ca9ebd_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_leafmoistu_zone_id_230676f2_fk_analytics",
        ),
        PrimaryKeyConstraint("id", name="analytics_leafmoisturesensor_pkey"),
        Index("analytics_leafmoisturesensor_user_id_46ca9ebd", "user_id"),
        Index("analytics_leafmoisturesensor_zone_id_230676f2", "zone_id"),
        Index(
            "ix_analytics_leafmoisturesensor_user_id_timestamp", "user_id", "timestamp"
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_leafmoisturesensor"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_leafmoisturesensor"
    )


class AnalyticsLeaftemperaturesensor(AgriBase, HasDeviceId):
    __tablename__ = "analytics_leaftemperaturesensor"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_leaftemper_user_id_a41024d0_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_leaftemper_zone_id_153f9604_fk_analytics",
        ),
        PrimaryKeyConstraint("id", name="analytics_leaftemperaturesensor_pkey"),
        Index("analytics_leaftemperaturesensor_user_id_a41024d0", "user_id"),
        Index("analytics_leaftemperaturesensor_zone_id_153f9604", "zone_id"),
        Index(
            "ix_analytics_leaftemperaturesensor_user_id_timestamp",
            "user_id",
            "timestamp",
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_leaftemperaturesensor"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_leaftemperaturesensor"
    )


class AnalyticsMultidepthsoilmoisturesensor(AgriBase, HasDeviceId):
    __tablename__ = "analytics_multidepthsoilmoisturesensor"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_multidepth_user_id_4ca851e7_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_multidepth_zone_id_27ad35eb_fk_analytics",
        ),
        PrimaryKeyConstraint("id", name="analytics_multidepthsoilmoisturesensor_pkey"),
        Index("analytics_multidepthsoilmoisturesensor_user_id_4ca851e7", "user_id"),
        Index("analytics_multidepthsoilmoisturesensor_zone_id_27ad35eb", "zone_id"),
        Index(
            "ix_analytics_multidepthsoilmoisturesensor_user_id_timestamp",
            "user_id",
            "timestamp",
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_multidepthsoilmoisturesensor"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_multidepthsoilmoisturesensor"
    )


class AnalyticsNpksensor(AgriBase, HasDeviceId):
    __tablename__ = "analytics_npksensor"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_npksensor_user_id_6182132e_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_npksensor_zone_id_75bfe336_fk_analytics_zone_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_npksensor_pkey"),
        Index("analytics_npksensor_user_id_6182132e", "user_id"),
        Index("analytics_npksensor_zone_id_75bfe336", "zone_id"),
        Index("ix_analytics_npksensor_user_id_timestamp", "user_id", "timestamp"),
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    nitrogen_color: Mapped[Optional[str]] = mapped_column(String(7))
    nitrogen_courbe_name: Mapped[Optional[str]] = mapped_column(String(50))
    nitrogen_value: Mapped[Optional[float]] = mapped_column(Double(53))
    phosphorus_color: Mapped[Optional[str]] = mapped_column(String(7))
    phosphorus_courbe_name: Mapped[Optional[str]] = mapped_column(String(50))
    phosphorus_value: Mapped[Optional[float]] = mapped_column(Double(53))
    potassium_color: Mapped[Optional[str]] = mapped_column(String(7))
    potassium_courbe_name: Mapped[Optional[str]] = mapped_column(String(50))
    potassium_value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_npksensor"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_npksensor"
    )


class AnalyticsPhsoil(AgriBase, HasDeviceId):
    __tablename__ = "analytics_phsoil"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_phsoil_user_id_c386a472_fk_CustomUser_customuser_id",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_phsoil_zone_id_20c52b80_fk_analytics_zone_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_phsoil_pkey"),
        Index("analytics_phsoil_user_id_c386a472", "user_id"),
        Index("analytics_phsoil_zone_id_20c52b80", "zone_id"),
        Index("ix_analytics_phsoil_user_id_timestamp", "user_id", "timestamp"),
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_phsoil"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_phsoil"
    )


class AnalyticsPhwatersensor(AgriBase, HasDeviceId):
    __tablename__ = "analytics_phwatersensor"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_phwatersen_user_id_cd0376cf_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_phwatersensor_zone_id_9e5c27b9_fk_analytics_zone_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_phwatersensor_pkey"),
        Index("analytics_phwatersensor_user_id_cd0376cf", "user_id"),
        Index("analytics_phwatersensor_zone_id_9e5c27b9", "zone_id"),
        Index("ix_analytics_phwatersensor_user_id_timestamp", "user_id", "timestamp"),
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_phwatersensor"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_phwatersensor"
    )


class AnalyticsPrecipitationrate(AgriBase, HasDeviceId):
    __tablename__ = "analytics_precipitationrate"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_precipitat_user_id_821ca5de_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_precipitat_zone_id_4575eb73_fk_analytics",
        ),
        PrimaryKeyConstraint("id", name="analytics_precipitationrate_pkey"),
        Index("analytics_precipitationrate_user_id_821ca5de", "user_id"),
        Index("analytics_precipitationrate_zone_id_4575eb73", "zone_id"),
        Index(
            "ix_analytics_precipitationrate_user_id_timestamp", "user_id", "timestamp"
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))
    color: Mapped[Optional[str]] = mapped_column(String(7))
    courbe_name: Mapped[Optional[str]] = mapped_column(String(50))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_precipitationrate"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_precipitationrate"
    )


class AnalyticsPressureweather(AgriBase, HasDeviceId):
    __tablename__ = "analytics_pressureweather"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_pressurewe_user_id_5de398f9_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_pressureweather_zone_id_7509a23b_fk_analytics_zone_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_pressureweather_pkey"),
        Index("analytics_pressureweather_user_id_5de398f9", "user_id"),
        Index("analytics_pressureweather_zone_id_7509a23b", "zone_id"),
        Index("ix_analytics_pressureweather_user_id_timestamp", "user_id", "timestamp"),
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_pressureweather"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_pressureweather"
    )


class AnalyticsSensorcolor(AgriBase):
    __tablename__ = "analytics_sensorcolor"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_sensorcolo_user_id_fbefb08e_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_sensorcolor_zone_id_9315ba34_fk_analytics_zone_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_sensorcolor_pkey"),
        Index("analytics_sensorcolor_user_id_fbefb08e", "user_id"),
        Index("analytics_sensorcolor_zone_id_9315ba34", "zone_id"),
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
    precipitation_rate_color: Mapped[str] = mapped_column(String(7), nullable=False)
    humidity_weather_color: Mapped[str] = mapped_column(String(7), nullable=False)
    wind_speed_color: Mapped[str] = mapped_column(String(7), nullable=False)
    solar_radiation_color: Mapped[str] = mapped_column(String(7), nullable=False)
    pressure_weather_color: Mapped[str] = mapped_column(String(7), nullable=False)
    wind_direction_color: Mapped[str] = mapped_column(String(7), nullable=False)
    temperature_weather_color: Mapped[str] = mapped_column(String(7), nullable=False)
    et0_color: Mapped[str] = mapped_column(String(7), nullable=False)
    ec_soil_medium_color: Mapped[str] = mapped_column(String(7), nullable=False)
    soil_temperature_medium_color: Mapped[str] = mapped_column(
        String(7), nullable=False
    )
    soil_ec_high_color: Mapped[str] = mapped_column(String(7), nullable=False)
    ec_soil_low_color: Mapped[str] = mapped_column(String(7), nullable=False)
    soil_moisture_medium_color: Mapped[str] = mapped_column(String(7), nullable=False)
    soil_moisture_high_color: Mapped[str] = mapped_column(String(7), nullable=False)
    soil_moisture_low_color: Mapped[str] = mapped_column(String(7), nullable=False)
    ph_soil_color: Mapped[str] = mapped_column(String(7), nullable=False)
    soil_temperature_low_color: Mapped[str] = mapped_column(String(7), nullable=False)
    soil_temperature_high_color: Mapped[str] = mapped_column(String(7), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[Optional[int]] = mapped_column(BigInteger)

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_sensorcolor"
    )
    zone: Mapped[Optional["AnalyticsZone"]] = relationship(
        "AnalyticsZone", back_populates="analytics_sensorcolor"
    )


class AnalyticsSensorlocation(AgriBase):
    __tablename__ = "analytics_sensorlocation"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_sensorloca_user_id_e60301ea_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_sensorlocation_zone_id_0608d7cc_fk_analytics_zone_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_sensorlocation_pkey"),
        Index("analytics_sensorlocation_user_id_e60301ea", "user_id"),
        Index("analytics_sensorlocation_zone_id_0608d7cc", "zone_id"),
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
    precipitation_rate_longitude: Mapped[float] = mapped_column(
        Double(53), nullable=False
    )
    precipitation_rate_latitude: Mapped[float] = mapped_column(
        Double(53), nullable=False
    )
    humidity_weather_longitude: Mapped[float] = mapped_column(
        Double(53), nullable=False
    )
    humidity_weather_latitude: Mapped[float] = mapped_column(Double(53), nullable=False)
    wind_speed_longitude: Mapped[float] = mapped_column(Double(53), nullable=False)
    wind_speed_latitude: Mapped[float] = mapped_column(Double(53), nullable=False)
    solar_radiation_longitude: Mapped[float] = mapped_column(Double(53), nullable=False)
    solar_radiation_latitude: Mapped[float] = mapped_column(Double(53), nullable=False)
    pressure_weather_longitude: Mapped[float] = mapped_column(
        Double(53), nullable=False
    )
    pressure_weather_latitude: Mapped[float] = mapped_column(Double(53), nullable=False)
    wind_direction_longitude: Mapped[float] = mapped_column(Double(53), nullable=False)
    wind_direction_latitude: Mapped[float] = mapped_column(Double(53), nullable=False)
    temperature_weather_longitude: Mapped[float] = mapped_column(
        Double(53), nullable=False
    )
    temperature_weather_latitude: Mapped[float] = mapped_column(
        Double(53), nullable=False
    )
    et0_longitude: Mapped[float] = mapped_column(Double(53), nullable=False)
    et0_latitude: Mapped[float] = mapped_column(Double(53), nullable=False)
    ec_soil_medium_longitude: Mapped[float] = mapped_column(Double(53), nullable=False)
    ec_soil_medium_latitude: Mapped[float] = mapped_column(Double(53), nullable=False)
    soil_temperature_medium_longitude: Mapped[float] = mapped_column(
        Double(53), nullable=False
    )
    soil_temperature_medium_latitude: Mapped[float] = mapped_column(
        Double(53), nullable=False
    )
    soil_ec_high_longitude: Mapped[float] = mapped_column(Double(53), nullable=False)
    soil_ec_high_latitude: Mapped[float] = mapped_column(Double(53), nullable=False)
    ec_soil_low_longitude: Mapped[float] = mapped_column(Double(53), nullable=False)
    ec_soil_low_latitude: Mapped[float] = mapped_column(Double(53), nullable=False)
    soil_moisture_medium_longitude: Mapped[float] = mapped_column(
        Double(53), nullable=False
    )
    soil_moisture_medium_latitude: Mapped[float] = mapped_column(
        Double(53), nullable=False
    )
    soil_moisture_high_longitude: Mapped[float] = mapped_column(
        Double(53), nullable=False
    )
    soil_moisture_high_latitude: Mapped[float] = mapped_column(
        Double(53), nullable=False
    )
    soil_moisture_low_longitude: Mapped[float] = mapped_column(
        Double(53), nullable=False
    )
    soil_moisture_low_latitude: Mapped[float] = mapped_column(
        Double(53), nullable=False
    )
    ph_soil_longitude: Mapped[float] = mapped_column(Double(53), nullable=False)
    ph_soil_latitude: Mapped[float] = mapped_column(Double(53), nullable=False)
    soil_temperature_low_longitude: Mapped[float] = mapped_column(
        Double(53), nullable=False
    )
    soil_temperature_low_latitude: Mapped[float] = mapped_column(
        Double(53), nullable=False
    )
    soil_temperature_high_longitude: Mapped[float] = mapped_column(
        Double(53), nullable=False
    )
    soil_temperature_high_latitude: Mapped[float] = mapped_column(
        Double(53), nullable=False
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_sensorlocation"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_sensorlocation"
    )


class AnalyticsSoilconductivitysensor(AgriBase, HasDeviceId):
    __tablename__ = "analytics_soilconductivitysensor"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_soilconduc_user_id_299beed3_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_soilconduc_zone_id_73a107a6_fk_analytics",
        ),
        PrimaryKeyConstraint("id", name="analytics_soilconductivitysensor_pkey"),
        Index("analytics_soilconductivitysensor_user_id_299beed3", "user_id"),
        Index("analytics_soilconductivitysensor_zone_id_73a107a6", "zone_id"),
        Index(
            "ix_analytics_soilconductivitysensor_user_id_timestamp",
            "user_id",
            "timestamp",
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_soilconductivitysensor"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_soilconductivitysensor"
    )


class AnalyticsSoilmoisturehigh(AgriBase, HasDeviceId):
    __tablename__ = "analytics_soilmoisturehigh"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_soilmoistu_user_id_463689ba_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_soilmoistu_zone_id_ef61097b_fk_analytics",
        ),
        PrimaryKeyConstraint("id", name="analytics_soilmoisturehigh_pkey"),
        Index("analytics_soilmoisturehigh_user_id_463689ba", "user_id"),
        Index("analytics_soilmoisturehigh_zone_id_ef61097b", "zone_id"),
        Index(
            "ix_analytics_soilmoisturehigh_user_id_timestamp", "user_id", "timestamp"
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_soilmoisturehigh"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_soilmoisturehigh"
    )


class AnalyticsSoilmoisturelow(AgriBase, HasDeviceId):
    __tablename__ = "analytics_soilmoisturelow"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_soilmoistu_user_id_963684b0_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_soilmoisturelow_zone_id_0fa3c886_fk_analytics_zone_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_soilmoisturelow_pkey"),
        Index("analytics_soilmoisturelow_user_id_963684b0", "user_id"),
        Index("analytics_soilmoisturelow_zone_id_0fa3c886", "zone_id"),
        Index("ix_analytics_soilmoisturelow_user_id_timestamp", "user_id", "timestamp"),
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_soilmoisturelow"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_soilmoisturelow"
    )


class AnalyticsSoilmoisturemedium(AgriBase, HasDeviceId):
    __tablename__ = "analytics_soilmoisturemedium"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_soilmoistu_user_id_20dd2643_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_soilmoistu_zone_id_e5bdf879_fk_analytics",
        ),
        PrimaryKeyConstraint("id", name="analytics_soilmoisturemedium_pkey"),
        Index("analytics_soilmoisturemedium_user_id_20dd2643", "user_id"),
        Index("analytics_soilmoisturemedium_zone_id_e5bdf879", "zone_id"),
        Index(
            "ix_analytics_soilmoisturemedium_user_id_timestamp", "user_id", "timestamp"
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_soilmoisturemedium"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_soilmoisturemedium"
    )


class AnalyticsSoilsalinitysensor(AgriBase, HasDeviceId):
    __tablename__ = "analytics_soilsalinitysensor"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_soilsalini_user_id_5f15cdf1_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_soilsalini_zone_id_ed078900_fk_analytics",
        ),
        PrimaryKeyConstraint("id", name="analytics_soilsalinitysensor_pkey"),
        Index("analytics_soilsalinitysensor_user_id_5f15cdf1", "user_id"),
        Index("analytics_soilsalinitysensor_zone_id_ed078900", "zone_id"),
        Index(
            "ix_analytics_soilsalinitysensor_user_id_timestamp", "user_id", "timestamp"
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_soilsalinitysensor"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_soilsalinitysensor"
    )


class AnalyticsSoiltemperaturehigh(AgriBase, HasDeviceId):
    __tablename__ = "analytics_soiltemperaturehigh"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_soiltemper_user_id_7bceb8cd_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_soiltemper_zone_id_a7604c73_fk_analytics",
        ),
        PrimaryKeyConstraint("id", name="analytics_soiltemperaturehigh_pkey"),
        Index("analytics_soiltemperaturehigh_user_id_7bceb8cd", "user_id"),
        Index("analytics_soiltemperaturehigh_zone_id_a7604c73", "zone_id"),
        Index(
            "ix_analytics_soiltemperaturehigh_user_id_timestamp", "user_id", "timestamp"
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_soiltemperaturehigh"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_soiltemperaturehigh"
    )


class AnalyticsSoiltemperaturelow(AgriBase, HasDeviceId):
    __tablename__ = "analytics_soiltemperaturelow"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_soiltemper_user_id_f2d8bcae_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_soiltemper_zone_id_da6a981f_fk_analytics",
        ),
        PrimaryKeyConstraint("id", name="analytics_soiltemperaturelow_pkey"),
        Index("analytics_soiltemperaturelow_user_id_f2d8bcae", "user_id"),
        Index("analytics_soiltemperaturelow_zone_id_da6a981f", "zone_id"),
        Index(
            "ix_analytics_soiltemperaturelow_user_id_timestamp", "user_id", "timestamp"
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_soiltemperaturelow"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_soiltemperaturelow"
    )


class AnalyticsSoiltemperaturemedium(AgriBase, HasDeviceId):
    __tablename__ = "analytics_soiltemperaturemedium"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_soiltemper_user_id_abc59db5_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_soiltemper_zone_id_f19fa4a1_fk_analytics",
        ),
        PrimaryKeyConstraint("id", name="analytics_soiltemperaturemedium_pkey"),
        Index("analytics_soiltemperaturemedium_user_id_abc59db5", "user_id"),
        Index("analytics_soiltemperaturemedium_zone_id_f19fa4a1", "zone_id"),
        Index(
            "ix_analytics_soiltemperaturemedium_user_id_timestamp",
            "user_id",
            "timestamp",
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_soiltemperaturemedium"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_soiltemperaturemedium"
    )


class AnalyticsSolarradiation(AgriBase, HasDeviceId):
    __tablename__ = "analytics_solarradiation"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_solarradia_user_id_9af11eae_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_solarradiation_zone_id_4b3654a3_fk_analytics_zone_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_solarradiation_pkey"),
        Index("analytics_solarradiation_user_id_9af11eae", "user_id"),
        Index("analytics_solarradiation_zone_id_4b3654a3", "zone_id"),
        Index("ix_analytics_solarradiation_user_id_timestamp", "user_id", "timestamp"),
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_solarradiation"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_solarradiation"
    )


class AnalyticsTemperatureweather(AgriBase, HasDeviceId):
    __tablename__ = "analytics_temperatureweather"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_temperatur_user_id_9da4f1c4_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_temperatur_zone_id_ea2d3879_fk_analytics",
        ),
        PrimaryKeyConstraint("id", name="analytics_temperatureweather_pkey"),
        Index("analytics_temperatureweather_user_id_9da4f1c4", "user_id"),
        Index("analytics_temperatureweather_zone_id_ea2d3879", "zone_id"),
        Index(
            "ix_analytics_temperatureweather_user_id_timestamp", "user_id", "timestamp"
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_temperatureweather"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_temperatureweather"
    )


class AnalyticsVpdweather(AgriBase, HasDeviceId):
    __tablename__ = "analytics_vpdweather"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_vpdweather_user_id_1bcf0232_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_vpdweather_zone_id_20bd35c6_fk_analytics_zone_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_vpdweather_pkey"),
        Index("analytics_vpdweather_user_id_1bcf0232", "user_id"),
        Index("analytics_vpdweather_zone_id_20bd35c6", "zone_id"),
        Index("ix_analytics_vpdweather_user_id_timestamp", "user_id", "timestamp"),
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_vpdweather"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_vpdweather"
    )


class AnalyticsWaterecsensor(AgriBase, HasDeviceId):
    __tablename__ = "analytics_waterecsensor"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_waterecsen_user_id_81437f78_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_waterecsensor_zone_id_810b7fa9_fk_analytics_zone_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_waterecsensor_pkey"),
        Index("analytics_waterecsensor_user_id_81437f78", "user_id"),
        Index("analytics_waterecsensor_zone_id_810b7fa9", "zone_id"),
        Index("ix_analytics_waterecsensor_user_id_timestamp", "user_id", "timestamp"),
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_waterecsensor"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_waterecsensor"
    )


class AnalyticsWaterflowsensor(AgriBase, HasDeviceId):
    __tablename__ = "analytics_waterflowsensor"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_waterflows_user_id_b6bbd62d_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_waterflowsensor_zone_id_e3e132c3_fk_analytics_zone_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_waterflowsensor_pkey"),
        Index("analytics_waterflowsensor_user_id_b6bbd62d", "user_id"),
        Index("analytics_waterflowsensor_zone_id_e3e132c3", "zone_id"),
        Index("ix_analytics_waterflowsensor_user_id_timestamp", "user_id", "timestamp"),
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_waterflowsensor"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_waterflowsensor"
    )


class AnalyticsWaterlevelsensor(AgriBase, HasDeviceId):
    __tablename__ = "analytics_waterlevelsensor"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_waterlevel_user_id_0881f5f0_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_waterlevel_zone_id_8e511e4f_fk_analytics",
        ),
        PrimaryKeyConstraint("id", name="analytics_waterlevelsensor_pkey"),
        Index("analytics_waterlevelsensor_user_id_0881f5f0", "user_id"),
        Index("analytics_waterlevelsensor_zone_id_8e511e4f", "zone_id"),
        Index(
            "ix_analytics_waterlevelsensor_user_id_timestamp", "user_id", "timestamp"
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_waterlevelsensor"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_waterlevelsensor"
    )


class AnalyticsWaterpressuresensor(AgriBase, HasDeviceId):
    __tablename__ = "analytics_waterpressuresensor"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_waterpress_user_id_4b65b052_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_waterpress_zone_id_62419baa_fk_analytics",
        ),
        PrimaryKeyConstraint("id", name="analytics_waterpressuresensor_pkey"),
        Index("analytics_waterpressuresensor_user_id_4b65b052", "user_id"),
        Index("analytics_waterpressuresensor_zone_id_62419baa", "zone_id"),
        Index(
            "ix_analytics_waterpressuresensor_user_id_timestamp", "user_id", "timestamp"
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_waterpressuresensor"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_waterpressuresensor"
    )


class AnalyticsWinddirection(AgriBase, HasDeviceId):
    __tablename__ = "analytics_winddirection"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_winddirect_user_id_1324bbbf_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_winddirection_zone_id_9c4ba837_fk_analytics_zone_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_winddirection_pkey"),
        Index("analytics_winddirection_user_id_1324bbbf", "user_id"),
        Index("analytics_winddirection_zone_id_9c4ba837", "zone_id"),
        Index("ix_analytics_winddirection_user_id_timestamp", "user_id", "timestamp"),
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_winddirection"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_winddirection"
    )


class AnalyticsWindspeed(AgriBase, HasDeviceId):
    __tablename__ = "analytics_windspeed"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_windspeed_user_id_88dc61be_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_windspeed_zone_id_90c76a35_fk_analytics_zone_id",
        ),
        PrimaryKeyConstraint("id", name="analytics_windspeed_pkey"),
        Index("analytics_windspeed_user_id_88dc61be", "user_id"),
        Index("analytics_windspeed_zone_id_90c76a35", "zone_id"),
        Index("ix_analytics_windspeed_user_id_timestamp", "user_id", "timestamp"),
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))

    user: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="analytics_windspeed"
    )
    zone: Mapped["AnalyticsZone"] = relationship(
        "AnalyticsZone", back_populates="analytics_windspeed"
    )


class AnalyticsKcperiodassignment(AgriBase):
    __tablename__ = "analytics_kcperiodassignment"
    __table_args__ = (
        ForeignKeyConstraint(
            ["kc_id"],
            ["analytics_kc.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_kcperiodassignment_kc_id_29f6608e_fk_analytics_kc_id",
        ),
        ForeignKeyConstraint(
            ["period_id"],
            ["analytics_kcperiod.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_kcperiodas_period_id_8c8ac2d4_fk_analytics",
        ),
        PrimaryKeyConstraint("id", name="analytics_kcperiodassignment_pkey"),
        Index("analytics_kcperiodassignment_kc_id_29f6608e", "kc_id"),
        Index("analytics_kcperiodassignment_period_id_8c8ac2d4", "period_id"),
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
    kc_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    period_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    kc: Mapped["AnalyticsKc"] = relationship(
        "AnalyticsKc", back_populates="analytics_kcperiodassignment"
    )
    period: Mapped["AnalyticsKcperiod"] = relationship(
        "AnalyticsKcperiod", back_populates="analytics_kcperiodassignment"
    )


class AnalyticsBatterysensor(AgriBase, HasDeviceId):
    """Device battery voltage (V) — reported by LoRaWAN nodes."""

    __tablename__ = "analytics_batterysensor"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_batterysensor_user_id_fk",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_batterysensor_zone_id_fk",
        ),
        PrimaryKeyConstraint("id", name="analytics_batterysensor_pkey"),
        Index("analytics_batterysensor_user_id", "user_id"),
        Index("analytics_batterysensor_zone_id", "zone_id"),
        Index("ix_analytics_batterysensor_user_id_timestamp", "user_id", "timestamp"),
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))


class AnalyticsSignalsensor(AgriBase, HasDeviceId):
    """Device radio signal strength, RSSI (dBm) — LoRaWAN nodes + Bivocom gateways."""

    __tablename__ = "analytics_signalsensor"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_signalsensor_user_id_fk",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_signalsensor_zone_id_fk",
        ),
        PrimaryKeyConstraint("id", name="analytics_signalsensor_pkey"),
        Index("analytics_signalsensor_user_id", "user_id"),
        Index("analytics_signalsensor_zone_id", "zone_id"),
        Index("ix_analytics_signalsensor_user_id_timestamp", "user_id", "timestamp"),
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
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    zone_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Double(53))


class AnalyticsSensorgroup(AgriBase):
    """A farmer-defined bundle of sensor streams, owned by the user account
    (which *is* the farm — one farm per account). Replaces the browser-local
    grouping of agri-web #64: groups now live server-side, so they survive a
    device change and are shared across every client of the same account.
    A group may span zones (and therefore sectors) within the farm; members are
    attached via ``AnalyticsSensorgroupsensor``. Deleting a group cascades to
    its membership rows only — devices and readings are never touched."""

    __tablename__ = "analytics_sensorgroup"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="analytics_sensorgroup_user_id_fk",
        ),
        PrimaryKeyConstraint("id", name="analytics_sensorgroup_pkey"),
        UniqueConstraint(
            "user_id", "name", name="analytics_sensorgroup_user_name_uniq"
        ),
        Index("analytics_sensorgroup_user_id_idx", "user_id"),
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
    # Farmer-visible group label; unique per owner (see the unique constraint).
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    # Optional free-text note shown in the group manager.
    description: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("''")
    )
    # Owner = the farm. Hard FK: CustomUser_customuser IS mirrored here.
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # Manual ordering of the groups in the UI (ties broken by name/id).
    display_order: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    # Hide a group without deleting it (keeps its membership rows).
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    sensors: Mapped[list["AnalyticsSensorgroupsensor"]] = relationship(
        "AnalyticsSensorgroupsensor", back_populates="group"
    )


class AnalyticsSensorgroupsensor(AgriBase):
    """One sensor stream inside a sensor group.

    A sensor stream is identified the way the whole platform identifies one
    since the device-keyed ownership refactor: the pair
    ``(device_id, sensor_key)`` — ``device_id`` being the soft FK to
    ``analytics_device`` carried by every reading row (see
    ``agri.db.base.HasDeviceId``) and ``sensor_key`` the canonical vocabulary
    from ``agri.core.alerts.SENSOR_KEY_REGISTRY`` that selects the reading
    table. ``device_id`` is therefore a SOFT FK (no DB constraint), matching
    both the readings and ``analytics_devicesensor``.

    The same stream MAY belong to several groups (groups are overlapping
    views, e.g. "Verger nord" and "Tous les tensiomètres"), so uniqueness is
    scoped to the group: a stream cannot be added twice to the SAME group."""

    __tablename__ = "analytics_sensorgroupsensor"
    __table_args__ = (
        ForeignKeyConstraint(
            ["group_id"],
            ["analytics_sensorgroup.id"],
            ondelete="CASCADE",
            deferrable=True,
            initially="DEFERRED",
            name="analytics_sensorgroupsensor_group_id_fk",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            ondelete="SET NULL",
            deferrable=True,
            initially="DEFERRED",
            name="analytics_sensorgroupsensor_zone_id_fk",
        ),
        PrimaryKeyConstraint("id", name="analytics_sensorgroupsensor_pkey"),
        UniqueConstraint(
            "group_id",
            "device_id",
            "sensor_key",
            name="analytics_sensorgroupsensor_group_sensor_uniq",
        ),
        Index("analytics_sensorgroupsensor_group_idx", "group_id"),
        Index(
            "analytics_sensorgroupsensor_sensor_idx",
            "device_id",
            "sensor_key",
        ),
        Index("analytics_sensorgroupsensor_zone_idx", "zone_id"),
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
    # Parent group; CASCADE so dropping a group drops only its membership rows.
    group_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # Soft FK to analytics_device (Django-managed, not mirrored here).
    device_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # Canonical sensor vocabulary (agri.core SENSOR_KEY_REGISTRY key).
    sensor_key: Mapped[str] = mapped_column(String(64), nullable=False)
    # Optional per-group display name overriding the registry label.
    label: Mapped[Optional[str]] = mapped_column(String(200))
    # Zone the stream is read from at add time — denormalized for display/
    # filtering only; ownership still resolves through analytics_device.
    zone_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    # Manual ordering of sensors within the group.
    display_order: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    group: Mapped["AnalyticsSensorgroup"] = relationship(
        "AnalyticsSensorgroup", back_populates="sensors"
    )
    zone: Mapped[Optional["AnalyticsZone"]] = relationship("AnalyticsZone")


class AnalyticsSensorcalibration(AgriBase):
    """Affine calibration of one sensor stream: ``real = raw * scale_a + offset_b``
    (agri-web #67). Keyed by the same ``(device_id, sensor_key)`` pair as
    ``AnalyticsSensorgroupsensor`` so both features address a sensor identically.
    STORAGE ONLY — applying the transform (and any unit conversion) lands later
    in agri-core; nothing here rewrites stored readings."""

    __tablename__ = "analytics_sensorcalibration"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="analytics_sensorcalibration_pkey"),
        # Exactly one calibration row per sensor stream.
        UniqueConstraint(
            "device_id",
            "sensor_key",
            name="analytics_sensorcalibration_sensor_uniq",
        ),
        Index("analytics_sensorcalibration_device_idx", "device_id"),
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
    # Soft FK to analytics_device (Django-managed, not mirrored here).
    device_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # Canonical sensor vocabulary (agri.core SENSOR_KEY_REGISTRY key).
    sensor_key: Mapped[str] = mapped_column(String(64), nullable=False)
    # Multiplicative term `a`; 1.0 = identity (no scaling).
    scale_a: Mapped[float] = mapped_column(
        Double(53), nullable=False, server_default=text("1.0")
    )
    # Additive term `b`, expressed in the target unit; 0.0 = no offset.
    offset_b: Mapped[float] = mapped_column(
        Double(53), nullable=False, server_default=text("0.0")
    )
    # Unit the corrected value is expressed in (free text, e.g. '°C', 'kPa').
    # Empty = keep the SENSOR_KEY_REGISTRY default unit for this sensor_key.
    unit: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("''")
    )
    # Turn the correction off without losing the coefficients.
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    # Optional note: who calibrated, against which reference instrument.
    note: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

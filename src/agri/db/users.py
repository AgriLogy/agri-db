"""SQLAlchemy mirror of the Django-managed user-auth tables.

Tables modeled here (all in the public schema of the live Supabase DB):
  * ``CustomUser_customuser``                        — the extended user table
  * ``CustomUser_customuser_groups``                 — M2M to auth_group
  * ``CustomUser_customuser_user_permissions``       — M2M to auth_permission

The FK targets (auth_group, auth_permission) are Django-managed; they are
NOT modeled in ``AgriBase.metadata`` and are filtered out of autogenerate
in ``_migrations/env.py``. SQLAlchemy stores the FK as a string reference
and does not require the target table to exist in metadata.

Initial content generated from the live Supabase dev DB via sqlacodegen,
then adapted to use ``AgriBase`` and our naming conventions.
"""

from __future__ import annotations

import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Double,
    ForeignKeyConstraint,
    Identity,
    Index,
    Integer,
    PrimaryKeyConstraint,
    SmallInteger,
    String,
    Table,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agri.db.base import AgriBase

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agri.db.analytics import (
        AnalyticsActivegraph,
        AnalyticsAlert,
        AnalyticsEcsalinitysensor,
        AnalyticsEcsoilhigh,
        AnalyticsEcsoillow,
        AnalyticsEcsoilmedium,
        AnalyticsElectricityconsumptionsensor,
        AnalyticsEt0calculated,
        AnalyticsEt0weather,
        AnalyticsFruitsizesensor,
        AnalyticsGraphname,
        AnalyticsHumidityweather,
        AnalyticsKc,
        AnalyticsLargefruitdiametersensor,
        AnalyticsLeafmoisturesensor,
        AnalyticsLeaftemperaturesensor,
        AnalyticsManageraffirmation,
        AnalyticsMultidepthsoilmoisturesensor,
        AnalyticsNotification,
        AnalyticsNpksensor,
        AnalyticsPhsoil,
        AnalyticsPhwatersensor,
        AnalyticsPrecipitationrate,
        AnalyticsPressureweather,
        AnalyticsSensorcolor,
        AnalyticsSensorlocation,
        AnalyticsSoilconductivitysensor,
        AnalyticsSoilmoisturehigh,
        AnalyticsSoilmoisturelow,
        AnalyticsSoilmoisturemedium,
        AnalyticsSoilsalinitysensor,
        AnalyticsSoiltemperaturehigh,
        AnalyticsSoiltemperaturelow,
        AnalyticsSoiltemperaturemedium,
        AnalyticsSolarradiation,
        AnalyticsTemperatureweather,
        AnalyticsUsersensorunitpreference,
        AnalyticsVpdweather,
        AnalyticsWaterecsensor,
        AnalyticsWaterflowsensor,
        AnalyticsWaterlevelsensor,
        AnalyticsWaterpressuresensor,
        AnalyticsWinddirection,
        AnalyticsWindspeed,
        AnalyticsZone,
    )


__all__ = [
    "CustomUserCustomuser",
    "CustomUserCustomuserGroups",
    "CustomUserCustomuserUserPermissions",
]


# ---------------------------------------------------------------------------
# Django-managed FK target stubs.
# ---------------------------------------------------------------------------
# `auth_group` and `auth_permission` are owned by Django; agri.db does NOT
# manage their schema. But the M2M tables below FK to them, and SQLAlchemy
# needs the target tables to be in the SAME MetaData as the source FK so
# ForeignKeyConstraint.referred_table resolves during DDL sort.
#
# We register bare stubs on `AgriBase.metadata` (just the `id` column for
# FK resolution) and rely on `_migrations/env.py:include_name` + `include_object`
# to skip them in autogenerate — filtered by the `auth_` name prefix on BOTH
# the reflected DB side and the metadata side.
auth_group = Table(
    "auth_group",
    AgriBase.metadata,
    Column("id", Integer, primary_key=True),
)

auth_permission = Table(
    "auth_permission",
    AgriBase.metadata,
    Column("id", Integer, primary_key=True),
)


class CustomUserCustomuser(AgriBase):
    """User account. Inherits Django's AbstractBaseUser + PermissionsMixin
    columns (id, password, last_login, is_superuser) plus the app-level
    fields (firstname, lastname, phone_number, geo coords, notification
    cadence)."""

    __tablename__ = "CustomUser_customuser"
    __table_args__ = (
        CheckConstraint(
            "notify_every >= 0",
            name="CustomUser_customuser_notify_every_check",
        ),
        PrimaryKeyConstraint("id", name="CustomUser_customuser_pkey"),
        UniqueConstraint("email", name="CustomUser_customuser_email_key"),
        UniqueConstraint("username", name="CustomUser_customuser_username_key"),
        # Django's `models.Index(fields=["-date_joined"])` → DESC ordering.
        # postgresql_ops is for operator classes, not sort direction; use
        # text("col DESC") so the expression matches the DB exactly.
        Index("CustomUser__date_jo_5319cf_idx", text("date_joined DESC")),
        Index("CustomUser__is_acti_d69f47_idx", "is_active"),
        Index(
            "CustomUser_customuser_email_4cbec7b5_like",
            "email",
            postgresql_ops={"email": "varchar_pattern_ops"},
        ),
        Index(
            "CustomUser_customuser_username_350c676a_like",
            "username",
            postgresql_ops={"username": "varchar_pattern_ops"},
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
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    firstname: Mapped[str] = mapped_column(String(100), nullable=False)
    lastname: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    payement_status: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_staff: Mapped[bool] = mapped_column(Boolean, nullable=False)
    # Technician RBAC flag (see agri.db.technicians). Added out-of-band on the
    # droplet by agri-api's ensure_technician_tables.py; absorbed into Alembic.
    # Like Django, the default (False) lives in the app layer, not the DB.
    is_technician: Mapped[bool] = mapped_column(Boolean, nullable=False)
    notify_every: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default=text("240")
    )
    # Preferred language for outbound notifications (and UI). 'fr' | 'ar'.
    preferred_language: Mapped[str] = mapped_column(
        String(8), nullable=False, server_default=text("'fr'")
    )
    date_joined: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    last_login: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    phone_number: Mapped[str | None] = mapped_column(String(15))
    latitude: Mapped[float | None] = mapped_column(Double(53))
    longitude: Mapped[float | None] = mapped_column(Double(53))
    last_notified: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    # Admin-controlled session kill switch. Any access/refresh token issued
    # (iat) before this timestamp is rejected, forcing the user to log out.
    # NULL = never revoked.
    sessions_revoked_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    # Backrefs from the M2M tables modeled below
    group_memberships: Mapped[list["CustomUserCustomuserGroups"]] = relationship(
        "CustomUserCustomuserGroups",
        back_populates="customuser",
        cascade="all, delete-orphan",
    )
    permission_grants: Mapped[list["CustomUserCustomuserUserPermissions"]] = (
        relationship(
            "CustomUserCustomuserUserPermissions",
            back_populates="customuser",
            cascade="all, delete-orphan",
        )
    )

    # ---------------------------------------------------------------------
    # Reverse side of every user-owned analytics relationship.
    #
    # Each analytics model declares a ``user`` relationship with
    # ``back_populates`` naming one of these attributes; SQLAlchemy pairs by
    # (target class, property name). Without these, configure_mappers()
    # raises for the WHOLE registry on the first ORM operation — so any
    # query through agri.core.database would fail. (sqlacodegen emitted both
    # sides; the hand-curated rewrite of this file dropped the user side.)
    #
    # Cross-file string targets resolve via the shared AgriBase registry —
    # both modules are imported in ``agri.db.__init__``.
    # ---------------------------------------------------------------------
    analytics_activegraph: Mapped[list["AnalyticsActivegraph"]] = relationship(
        "AnalyticsActivegraph", back_populates="user"
    )
    analytics_alert: Mapped[list["AnalyticsAlert"]] = relationship(
        "AnalyticsAlert", back_populates="user"
    )
    analytics_ecsalinitysensor: Mapped[list["AnalyticsEcsalinitysensor"]] = (
        relationship("AnalyticsEcsalinitysensor", back_populates="user")
    )
    analytics_ecsoilhigh: Mapped[list["AnalyticsEcsoilhigh"]] = relationship(
        "AnalyticsEcsoilhigh", back_populates="user"
    )
    analytics_ecsoillow: Mapped[list["AnalyticsEcsoillow"]] = relationship(
        "AnalyticsEcsoillow", back_populates="user"
    )
    analytics_ecsoilmedium: Mapped[list["AnalyticsEcsoilmedium"]] = relationship(
        "AnalyticsEcsoilmedium", back_populates="user"
    )
    analytics_electricityconsumptionsensor: Mapped[
        list["AnalyticsElectricityconsumptionsensor"]
    ] = relationship("AnalyticsElectricityconsumptionsensor", back_populates="user")
    analytics_et0calculated: Mapped[list["AnalyticsEt0calculated"]] = relationship(
        "AnalyticsEt0calculated", back_populates="user"
    )
    analytics_et0weather: Mapped[list["AnalyticsEt0weather"]] = relationship(
        "AnalyticsEt0weather", back_populates="user"
    )
    analytics_fruitsizesensor: Mapped[list["AnalyticsFruitsizesensor"]] = relationship(
        "AnalyticsFruitsizesensor", back_populates="user"
    )
    analytics_graphname: Mapped[list["AnalyticsGraphname"]] = relationship(
        "AnalyticsGraphname", back_populates="user"
    )
    analytics_humidityweather: Mapped[list["AnalyticsHumidityweather"]] = relationship(
        "AnalyticsHumidityweather", back_populates="user"
    )
    analytics_kc: Mapped[list["AnalyticsKc"]] = relationship(
        "AnalyticsKc", back_populates="user"
    )
    analytics_largefruitdiametersensor: Mapped[
        list["AnalyticsLargefruitdiametersensor"]
    ] = relationship("AnalyticsLargefruitdiametersensor", back_populates="user")
    analytics_leafmoisturesensor: Mapped[list["AnalyticsLeafmoisturesensor"]] = (
        relationship("AnalyticsLeafmoisturesensor", back_populates="user")
    )
    analytics_leaftemperaturesensor: Mapped[list["AnalyticsLeaftemperaturesensor"]] = (
        relationship("AnalyticsLeaftemperaturesensor", back_populates="user")
    )
    analytics_multidepthsoilmoisturesensor: Mapped[
        list["AnalyticsMultidepthsoilmoisturesensor"]
    ] = relationship("AnalyticsMultidepthsoilmoisturesensor", back_populates="user")
    analytics_notification: Mapped[list["AnalyticsNotification"]] = relationship(
        "AnalyticsNotification", back_populates="user"
    )
    analytics_npksensor: Mapped[list["AnalyticsNpksensor"]] = relationship(
        "AnalyticsNpksensor", back_populates="user"
    )
    analytics_phsoil: Mapped[list["AnalyticsPhsoil"]] = relationship(
        "AnalyticsPhsoil", back_populates="user"
    )
    analytics_phwatersensor: Mapped[list["AnalyticsPhwatersensor"]] = relationship(
        "AnalyticsPhwatersensor", back_populates="user"
    )
    analytics_precipitationrate: Mapped[list["AnalyticsPrecipitationrate"]] = (
        relationship("AnalyticsPrecipitationrate", back_populates="user")
    )
    analytics_pressureweather: Mapped[list["AnalyticsPressureweather"]] = relationship(
        "AnalyticsPressureweather", back_populates="user"
    )
    analytics_sensorcolor: Mapped[list["AnalyticsSensorcolor"]] = relationship(
        "AnalyticsSensorcolor", back_populates="user"
    )
    analytics_sensorlocation: Mapped[list["AnalyticsSensorlocation"]] = relationship(
        "AnalyticsSensorlocation", back_populates="user"
    )
    analytics_soilconductivitysensor: Mapped[
        list["AnalyticsSoilconductivitysensor"]
    ] = relationship("AnalyticsSoilconductivitysensor", back_populates="user")
    analytics_soilmoisturehigh: Mapped[list["AnalyticsSoilmoisturehigh"]] = (
        relationship("AnalyticsSoilmoisturehigh", back_populates="user")
    )
    analytics_soilmoisturelow: Mapped[list["AnalyticsSoilmoisturelow"]] = relationship(
        "AnalyticsSoilmoisturelow", back_populates="user"
    )
    analytics_soilmoisturemedium: Mapped[list["AnalyticsSoilmoisturemedium"]] = (
        relationship("AnalyticsSoilmoisturemedium", back_populates="user")
    )
    analytics_soilsalinitysensor: Mapped[list["AnalyticsSoilsalinitysensor"]] = (
        relationship("AnalyticsSoilsalinitysensor", back_populates="user")
    )
    analytics_soiltemperaturehigh: Mapped[list["AnalyticsSoiltemperaturehigh"]] = (
        relationship("AnalyticsSoiltemperaturehigh", back_populates="user")
    )
    analytics_soiltemperaturelow: Mapped[list["AnalyticsSoiltemperaturelow"]] = (
        relationship("AnalyticsSoiltemperaturelow", back_populates="user")
    )
    analytics_soiltemperaturemedium: Mapped[list["AnalyticsSoiltemperaturemedium"]] = (
        relationship("AnalyticsSoiltemperaturemedium", back_populates="user")
    )
    analytics_solarradiation: Mapped[list["AnalyticsSolarradiation"]] = relationship(
        "AnalyticsSolarradiation", back_populates="user"
    )
    analytics_temperatureweather: Mapped[list["AnalyticsTemperatureweather"]] = (
        relationship("AnalyticsTemperatureweather", back_populates="user")
    )
    analytics_usersensorunitpreference: Mapped[
        list["AnalyticsUsersensorunitpreference"]
    ] = relationship("AnalyticsUsersensorunitpreference", back_populates="user")
    analytics_vpdweather: Mapped[list["AnalyticsVpdweather"]] = relationship(
        "AnalyticsVpdweather", back_populates="user"
    )
    analytics_waterecsensor: Mapped[list["AnalyticsWaterecsensor"]] = relationship(
        "AnalyticsWaterecsensor", back_populates="user"
    )
    analytics_waterflowsensor: Mapped[list["AnalyticsWaterflowsensor"]] = relationship(
        "AnalyticsWaterflowsensor", back_populates="user"
    )
    analytics_waterlevelsensor: Mapped[list["AnalyticsWaterlevelsensor"]] = (
        relationship("AnalyticsWaterlevelsensor", back_populates="user")
    )
    analytics_waterpressuresensor: Mapped[list["AnalyticsWaterpressuresensor"]] = (
        relationship("AnalyticsWaterpressuresensor", back_populates="user")
    )
    analytics_winddirection: Mapped[list["AnalyticsWinddirection"]] = relationship(
        "AnalyticsWinddirection", back_populates="user"
    )
    analytics_windspeed: Mapped[list["AnalyticsWindspeed"]] = relationship(
        "AnalyticsWindspeed", back_populates="user"
    )
    analytics_zone: Mapped[list["AnalyticsZone"]] = relationship(
        "AnalyticsZone", back_populates="user"
    )
    # ManagerAffirmation has two FKs to the user, so each reverse side names
    # the foreign key it pairs with.
    analytics_manageraffirmation_decided_by: Mapped[
        list["AnalyticsManageraffirmation"]
    ] = relationship(
        "AnalyticsManageraffirmation",
        foreign_keys="AnalyticsManageraffirmation.decided_by_id",
        back_populates="decided_by",
    )
    analytics_manageraffirmation_requested_by: Mapped[
        list["AnalyticsManageraffirmation"]
    ] = relationship(
        "AnalyticsManageraffirmation",
        foreign_keys="AnalyticsManageraffirmation.requested_by_id",
        back_populates="requested_by",
    )


class CustomUserCustomuserGroups(AgriBase):
    """Junction: user ↔ auth_group. auth_group itself is Django-managed
    and not modeled here; the FK is kept as an opaque integer reference."""

    __tablename__ = "CustomUser_customuser_groups"
    __table_args__ = (
        ForeignKeyConstraint(
            ["customuser_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="CustomUser_customuse_customuser_id_905286ba_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["group_id"],
            ["auth_group.id"],
            deferrable=True,
            initially="DEFERRED",
            name="CustomUser_customuser_groups_group_id_0fbcb83a_fk_auth_group_id",
        ),
        PrimaryKeyConstraint("id", name="CustomUser_customuser_groups_pkey"),
        UniqueConstraint(
            "customuser_id",
            "group_id",
            name="CustomUser_customuser_gr_customuser_id_group_id_b93892d6_uniq",
        ),
        Index(
            "CustomUser_customuser_groups_customuser_id_905286ba",
            "customuser_id",
        ),
        Index(
            "CustomUser_customuser_groups_group_id_0fbcb83a",
            "group_id",
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
    customuser_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    group_id: Mapped[int] = mapped_column(Integer, nullable=False)

    customuser: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="group_memberships"
    )


class CustomUserCustomuserUserPermissions(AgriBase):
    """Junction: user ↔ auth_permission. auth_permission itself is
    Django-managed and not modeled here."""

    __tablename__ = "CustomUser_customuser_user_permissions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["customuser_id"],
            ["CustomUser_customuser.id"],
            deferrable=True,
            initially="DEFERRED",
            name="CustomUser_customuse_customuser_id_37c73c20_fk_CustomUse",
        ),
        ForeignKeyConstraint(
            ["permission_id"],
            ["auth_permission.id"],
            deferrable=True,
            initially="DEFERRED",
            name="CustomUser_customuse_permission_id_a600872b_fk_auth_perm",
        ),
        PrimaryKeyConstraint("id", name="CustomUser_customuser_user_permissions_pkey"),
        UniqueConstraint(
            "customuser_id",
            "permission_id",
            name="CustomUser_customuser_us_customuser_id_permission_4674fd8b_uniq",
        ),
        Index(
            "CustomUser_customuser_user_permissions_customuser_id_37c73c20",
            "customuser_id",
        ),
        Index(
            "CustomUser_customuser_user_permissions_permission_id_a600872b",
            "permission_id",
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
    customuser_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    permission_id: Mapped[int] = mapped_column(Integer, nullable=False)

    customuser: Mapped["CustomUserCustomuser"] = relationship(
        "CustomUserCustomuser", back_populates="permission_grants"
    )

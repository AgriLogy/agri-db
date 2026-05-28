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
    MetaData,
    PrimaryKeyConstraint,
    SmallInteger,
    String,
    Table,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agri.db.base import AgriBase

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
    notify_every: Mapped[int] = mapped_column(SmallInteger, nullable=False)
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

    # Backrefs from the M2M tables modeled below
    group_memberships: Mapped[list["CustomUserCustomuserGroups"]] = relationship(
        "CustomUserCustomuserGroups",
        back_populates="customuser",
        cascade="all, delete-orphan",
    )
    permission_grants: Mapped[list["CustomUserCustomuserUserPermissions"]] = relationship(
        "CustomUserCustomuserUserPermissions",
        back_populates="customuser",
        cascade="all, delete-orphan",
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
        PrimaryKeyConstraint(
            "id", name="CustomUser_customuser_user_permissions_pkey"
        ),
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

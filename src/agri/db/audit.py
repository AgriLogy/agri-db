"""SQLAlchemy mirrors of the back-office audit / monitoring / settings tables.

Absorbed from agri-api's out-of-band boot scripts
``back/scripts/ensure_admin_tables.py`` (``AuditEvent`` / ``SystemSetting``) and
``back/scripts/ensure_monitoring_tables.py`` (``TaskRun`` /
``NotificationDeliveryLog`` / ``LoginEvent``). Byte-matches the live droplet
schema: all ``*_id`` relations are ORM-level in agri-api (Django
``db_constraint=False``) so there are NO DB-level foreign keys, and Django
keeps defaults in the app layer so there are no DB defaults either.
"""
from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Identity,
    Integer,
    PrimaryKeyConstraint,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from agri.db.base import AgriBase


class AnalyticsAuditevent(AgriBase):
    """An admin-action audit record (who changed what, when)."""

    __tablename__ = 'analytics_auditevent'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='analytics_auditevent_pkey'),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1),
        primary_key=True,
    )
    actor_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    target_type: Mapped[str] = mapped_column(String(64), nullable=False)
    target_id: Mapped[str] = mapped_column(String(64), nullable=False)
    changes: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))


class AnalyticsSystemsetting(AgriBase):
    """A categorized key/value system setting."""

    __tablename__ = 'analytics_systemsetting'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='analytics_systemsetting_pkey'),
        UniqueConstraint('key', name='analytics_systemsetting_key_key'),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1),
        primary_key=True,
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))


class AnalyticsTaskrun(AgriBase):
    """One Celery task execution, written centrally from Celery signals."""

    __tablename__ = 'analytics_taskrun'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='analytics_taskrun_pkey'),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1),
        primary_key=True,
    )
    task_name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)  # success|failure
    started_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    finished_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    runtime_ms: Mapped[Optional[int]] = mapped_column(Integer)
    result: Mapped[dict] = mapped_column(JSONB, nullable=False)
    error: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))


class AnalyticsNotificationdeliverylog(AgriBase):
    """One notification delivery attempt (email / SMS / WhatsApp)."""

    __tablename__ = 'analytics_notificationdeliverylog'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='analytics_notificationdeliverylog_pkey'),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1),
        primary_key=True,
    )
    channel: Mapped[str] = mapped_column(String(16), nullable=False)  # email|sms|whatsapp
    kind: Mapped[str] = mapped_column(String(24), nullable=False)
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(String(12), nullable=False)  # sent|failed|skipped
    error: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))


class AnalyticsLoginevent(AgriBase):
    """One user sign-in attempt (success or failure)."""

    __tablename__ = 'analytics_loginevent'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='analytics_loginevent_pkey'),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1),
        primary_key=True,
    )
    username: Mapped[str] = mapped_column(String(150), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    ip: Mapped[str] = mapped_column(String(64), nullable=False)
    user_agent: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

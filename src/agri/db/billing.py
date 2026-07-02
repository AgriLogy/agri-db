"""SQLAlchemy mirrors of the billing tables (plans / subscriptions / invoices).

Absorbed from agri-api's out-of-band boot script
``back/scripts/ensure_admin_tables.py`` (Django ``apps.irrigation.models``:
``Plan`` / ``Subscription`` / ``Invoice``). Column shapes byte-match the live
droplet schema: the Django models declare every relation with
``db_constraint=False``, so there are NO DB-level foreign keys here on purpose
— the relations are enforced at the ORM level in agri-api. Likewise Django
puts defaults in the app layer, not the DB, so no ``server_default`` either.
"""
from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Double,
    Identity,
    PrimaryKeyConstraint,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from agri.db.base import AgriBase


class AnalyticsPlan(AgriBase):
    """A billable subscription plan."""

    __tablename__ = 'analytics_plan'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='analytics_plan_pkey'),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price_dh: Mapped[float] = mapped_column(Double(53), nullable=False)
    interval: Mapped[str] = mapped_column(String(16), nullable=False)  # monthly|yearly
    features: Mapped[list] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))


class AnalyticsSubscription(AgriBase):
    """A customer's subscription to a plan (user_id / plan_id are ORM-level
    relations in agri-api — no DB constraint by design)."""

    __tablename__ = 'analytics_subscription'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='analytics_subscription_pkey'),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    plan_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(String(16), nullable=False)  # active|cancelled|expired
    period_start: Mapped[Optional[datetime.date]] = mapped_column(Date)
    period_end: Mapped[Optional[datetime.date]] = mapped_column(Date)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))


class AnalyticsInvoice(AgriBase):
    """An invoice issued against a subscription."""

    __tablename__ = 'analytics_invoice'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='analytics_invoice_pkey'),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1),
        primary_key=True,
    )
    subscription_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    amount_dh: Mapped[float] = mapped_column(Double(53), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)  # paid|unpaid
    issued_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    paid_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

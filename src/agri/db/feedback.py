"""SQLAlchemy mirror of the ``feedback_bugreport`` table.

Stores in-app "Report an issue" submissions from the farmer web app: the
free-text report plus rich client context (route, browser, OS, viewport, app
version, ...) and an optional Cloudinary screen-recording URL. Written by the
agri-api ``apps.feedback`` router and surfaced read/write in the admin
back-office through the generic ``/api/admin/db`` CRUD.
"""
from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
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


class FeedbackBugreport(AgriBase):
    __tablename__ = 'feedback_bugreport'
    __table_args__ = (
        ForeignKeyConstraint(
            ['user_id'],
            ['CustomUser_customuser.id'],
            deferrable=True,
            initially='DEFERRED',
            name='feedback_bugreport_user_id_fkey',
        ),
        PrimaryKeyConstraint('id', name='feedback_bugreport_pkey'),
        Index('feedback_bugreport_user_id_idx', 'user_id'),
        Index('feedback_bugreport_status_idx', 'status'),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1),
        primary_key=True,
    )
    report_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'bug'"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'open'"))
    video_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    user_email: Mapped[str] = mapped_column(String(254), nullable=False, server_default=text("''"))
    page_url: Mapped[str] = mapped_column(String(1000), nullable=False, server_default=text("''"))
    route: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("''"))
    module: Mapped[str] = mapped_column(String(100), nullable=False, server_default=text("''"))
    environment: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("''"))
    app_version: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("''"))
    browser: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("''"))
    os: Mapped[str] = mapped_column(String(100), nullable=False, server_default=text("''"))
    context: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False, server_default=text('now()')
    )
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), nullable=True)

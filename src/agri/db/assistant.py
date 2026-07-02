"""SQLAlchemy mirrors of the assistant tables.

Absorbed from agri-api's out-of-band boot script
``back/scripts/ensure_assistant_tables.py`` (Django ``apps.assistant.models``:
``AssistantConversation`` / ``ProactiveNotice``). Byte-matches the live droplet
schema: ``user_id`` is an ORM-level relation in agri-api (Django
``db_constraint=False``) so there are NO DB-level foreign keys, and no DB
defaults.

Note: the current Django ``AssistantConversation`` model declares a
``(user, -updated_at)`` index that does NOT exist on the live table (the
ensure script only creates missing tables, never alters existing ones), so it
is intentionally not modeled here — the schema-of-record matches reality.
"""

from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    Identity,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from agri.db.base import AgriBase


class AssistantConversation(AgriBase):
    """One assistant conversation per row, messages stored as a JSON list.

    ``client_id`` is the frontend-generated id, so a conversation keeps a
    stable identity whether first created offline (localStorage) or on the
    server — sync upserts by (user, client_id).
    """

    __tablename__ = "assistant_conversation"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="assistant_conversation_pkey"),
        UniqueConstraint("user_id", "client_id", name="uniq_user_client_conversation"),
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
    # Frontend-generated conversation id (stable across devices/offline).
    client_id: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    # [{id, role, content, card?, timestamp}, ...]
    messages: Mapped[list] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )


class AssistantProactiveNotice(AgriBase):
    """Dedup ledger for the proactive-insight scan — one row per user holding
    the last time a proactive notification was pushed (cooldown window)."""

    __tablename__ = "assistant_proactive_notice"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="assistant_proactive_notice_pkey"),
        UniqueConstraint("user_id", name="assistant_proactive_notice_user_id_key"),
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
    last_sent: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

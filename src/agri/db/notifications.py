"""Mobile push registration (agri-api #37: push notifications via FCM).

``notification_push_token`` holds one row per app install that has granted
notification permission. The apps (agri-mobile, agri-ios) obtain an FCM
registration token from Firebase and POST it to agri-api; when an alert
triggers, agri-api sends an FCM message to every token of the alert's owner.

* ``token``        — FCM registration token. Unique: a token belongs to one
                     install, and re-registering it under another account
                     moves it (the last signed-in user owns the device).
* ``platform``     — android | ios | web (CHECK).
* ``last_seen_at`` — refreshed on every re-registration. FCM tokens go stale;
                     the sender also deletes a token as soon as FCM reports it
                     UNREGISTERED.

Like the rest of the schema, ``user_id`` has no DB-level foreign key: the app
layer enforces ownership and removes a user's tokens with the account.
"""

from __future__ import annotations

import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Identity,
    Index,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from agri.db.base import AgriBase

PUSH_PLATFORMS = ("android", "ios", "web")


class NotificationPushToken(AgriBase):
    """One app install registered for push (FCM registration token)."""

    __tablename__ = "notification_push_token"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="notification_push_token_pkey"),
        UniqueConstraint("token", name="notification_push_token_token_key"),
        CheckConstraint(
            "platform IN ('android', 'ios', 'web')",
            name="notification_push_token_platform_check",
        ),
        Index("notification_push_token_user_idx", "user_id"),
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
    token: Mapped[str] = mapped_column(String(512), nullable=False)
    platform: Mapped[str] = mapped_column(String(16), nullable=False)
    app_version: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("''")
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )
    last_seen_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )


__all__ = ["PUSH_PLATFORMS", "NotificationPushToken"]

"""add alert notify_email + notify_whatsapp columns

Per-alert delivery-channel selection. Mirrors the Django model fields
``Alert.notify_email`` / ``Alert.notify_whatsapp`` and the agri-db SQLAlchemy
mirror (``AnalyticsAlert``). Email defaults on (existing behaviour); WhatsApp
defaults off. Idempotent ``IF NOT EXISTS`` so re-running after a Django
``migrate`` is a no-op.

Revision ID: c4d8e1f02a37
Revises: b7f2a4c1d9e3
Create Date: 2026-06-10 09:00:00.000000+00:00
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op


revision: str = "c4d8e1f02a37"
down_revision: Union[str, None] = "b7f2a4c1d9e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE analytics_alert "
        "ADD COLUMN IF NOT EXISTS notify_email BOOLEAN NOT NULL DEFAULT TRUE"
    )
    op.execute(
        "ALTER TABLE analytics_alert "
        "ADD COLUMN IF NOT EXISTS notify_whatsapp BOOLEAN NOT NULL DEFAULT FALSE"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE analytics_alert DROP COLUMN IF EXISTS notify_whatsapp")
    op.execute("ALTER TABLE analytics_alert DROP COLUMN IF EXISTS notify_email")

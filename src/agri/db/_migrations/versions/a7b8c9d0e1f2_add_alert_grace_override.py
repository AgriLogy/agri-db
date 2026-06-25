"""add alert grace_override_seconds column

Per-alert grace override (agri-api #37): ``ALERT_GRACE_PERIODS`` is global per
sensor key. ``grace_override_seconds`` lets one alert ask for a tighter (or
looser) re-notify cadence than its sensor's default — e.g. "ping me every
minute for this one critical alert". NULL = use the global per-key value.

Idempotent ``ADD COLUMN IF NOT EXISTS`` so re-running after a Django
``migrate`` is a no-op.

Revision ID: a7b8c9d0e1f2
Revises: f3a4b5c6d7e8
Create Date: 2026-06-25 23:10:00.000000+00:00
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op


revision: str = "a7b8c9d0e1f2"
down_revision: Union[str, None] = "f3a4b5c6d7e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE analytics_alert "
        "ADD COLUMN IF NOT EXISTS grace_override_seconds INTEGER"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE analytics_alert DROP COLUMN IF EXISTS grace_override_seconds")

"""add analytics_device.latitude / longitude

Stores each device's GPS position (WGS-84 decimal degrees) so the farmer map
can plot every sensor at its real location instead of a hand-drawn placeholder
(MAP-1). Both columns are NULLABLE — existing devices have no coordinates until
they are captured at onboarding or set from the admin device list.

Revision ID: b2c3d4e5f6a7
Revises: 135b18a7441b
Create Date: 2026-07-16 00:00:00.000000+00:00
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "135b18a7441b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE analytics_device "
        "ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION"
    )
    op.execute(
        "ALTER TABLE analytics_device "
        "ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE analytics_device DROP COLUMN IF EXISTS longitude")
    op.execute("ALTER TABLE analytics_device DROP COLUMN IF EXISTS latitude")

"""add rectangular basin dimensions to analytics_zone

Rectangular basin geometry for the ultrasonic water-level widget:
length x width x H_tot (sensor plane to bottom). Restores the legacy trio
(basin_max_depth_m / basin_area_m2 / sensor_mount_offset_m, idempotent) and
adds basin_length_m / basin_width_m / basin_height_m. Mirrors the Django
``Zone`` fields (analytics migration 0068). Idempotent ``IF NOT EXISTS``.

Revision ID: f5a6b7c8d9e0
Revises: b8c2f0d5e713
Create Date: 2026-10-05 00:00:00.000000+00:00
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op


revision: str = "f5a6b7c8d9e0"
down_revision: Union[str, None] = "b8c2f0d5e713"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE analytics_zone "
        "ADD COLUMN IF NOT EXISTS basin_max_depth_m DOUBLE PRECISION"
    )
    op.execute(
        "ALTER TABLE analytics_zone "
        "ADD COLUMN IF NOT EXISTS basin_area_m2 DOUBLE PRECISION"
    )
    op.execute(
        "ALTER TABLE analytics_zone "
        "ADD COLUMN IF NOT EXISTS sensor_mount_offset_m DOUBLE PRECISION"
    )
    op.execute(
        "ALTER TABLE analytics_zone "
        "ADD COLUMN IF NOT EXISTS basin_length_m DOUBLE PRECISION"
    )
    op.execute(
        "ALTER TABLE analytics_zone "
        "ADD COLUMN IF NOT EXISTS basin_width_m DOUBLE PRECISION"
    )
    op.execute(
        "ALTER TABLE analytics_zone "
        "ADD COLUMN IF NOT EXISTS basin_height_m DOUBLE PRECISION"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE analytics_zone DROP COLUMN IF EXISTS basin_height_m"
    )
    op.execute(
        "ALTER TABLE analytics_zone DROP COLUMN IF EXISTS basin_width_m"
    )
    op.execute(
        "ALTER TABLE analytics_zone DROP COLUMN IF EXISTS basin_length_m"
    )

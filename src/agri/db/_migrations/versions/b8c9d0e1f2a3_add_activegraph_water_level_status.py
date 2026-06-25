"""add analytics_activegraph.water_level_status

Per-zone visibility flag for the water-level dashboard section (agrilogy-front
#4 follow-up), mirroring the existing ``*_status`` toggles on
``analytics_activegraph`` (e.g. ``water_pressure_status``). Defaults off so
existing zones are unchanged until the section is enabled. Idempotent
``IF NOT EXISTS`` so re-running after a Django ``migrate`` is a no-op.

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-06-26 00:00:00.000000+00:00
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op


revision: str = "b8c9d0e1f2a3"
down_revision: Union[str, None] = "a7b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE analytics_activegraph "
        "ADD COLUMN IF NOT EXISTS water_level_status BOOLEAN NOT NULL DEFAULT FALSE"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE analytics_activegraph DROP COLUMN IF EXISTS water_level_status"
    )

"""default analytics_activegraph.water_level_status to TRUE + backfill

The water-level dashboard section was shipped opt-in (default FALSE), but every
other ``*_status`` toggle on ``analytics_activegraph`` defaults TRUE. Align it:
flip the column default to TRUE and backfill existing rows so the section shows
for current zones. Idempotent.

Revision ID: c9d0e1f2a3b4
Revises: b8c9d0e1f2a3
Create Date: 2026-06-26 01:00:00.000000+00:00
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op


revision: str = "c9d0e1f2a3b4"
down_revision: Union[str, None] = "b8c9d0e1f2a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE analytics_activegraph "
        "ALTER COLUMN water_level_status SET DEFAULT TRUE"
    )
    op.execute(
        "UPDATE analytics_activegraph "
        "SET water_level_status = TRUE WHERE water_level_status = FALSE"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE analytics_activegraph "
        "ALTER COLUMN water_level_status SET DEFAULT FALSE"
    )

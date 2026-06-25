"""add analytics_zone.elevation_m + merge divergent heads

Adds ``elevation_m`` (metres above sea level, default 0) to ``analytics_zone``
so the agronomy clear-sky radiation term ``Rso = (0.75 + 2e-5 * elevation_m)
* Ra`` is correct away from sea level (agri-api issue #15).

This migration also **merges** the three heads that diverged off
``31d37a9a428c`` (each a separately-merged feature branch):
  * ``a1b2c3d4e5f6`` — CustomUser.sessions_revoked_at
  * ``c4d8e1f02a37`` — alert notify_email/notify_whatsapp
  * ``c7e1a9f3b502`` — notify_every hours -> minutes
so ``alembic upgrade head`` resolves to a single linear head again. The merge
carries no schema change of its own beyond the elevation column; the heads
touched disjoint tables so unifying them is purely a revision-graph fix.

Revision ID: d1e2f3a4b5c6
Revises: a1b2c3d4e5f6, c4d8e1f02a37, c7e1a9f3b502
Create Date: 2026-06-25 16:40:00.000000+00:00
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op


revision: str = "d1e2f3a4b5c6"
down_revision: Union[str, Sequence[str], None] = (
    "a1b2c3d4e5f6",
    "c4d8e1f02a37",
    "c7e1a9f3b502",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE analytics_zone "
        "ADD COLUMN IF NOT EXISTS elevation_m DOUBLE PRECISION NOT NULL DEFAULT 0"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE analytics_zone DROP COLUMN IF EXISTS elevation_m")

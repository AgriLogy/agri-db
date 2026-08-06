"""add sector geometry, area, perimeter and colour

Sector polygons currently live in the BROWSER: agri-web writes them to
``localStorage`` under ``agrilogy-farm-sectors-v1`` and nothing reaches the
server. ``analytics_sector`` is a name-only bucket, so a farm's sectors are
per-device and per-browser — clearing the cache destroys them, a second device
sees none of them, and nothing server-side (area, satellite statistics,
per-sector irrigation) can key off the shape. This makes the geometry
server-owned.

Columns:

* ``geometry``    — GeoJSON Polygon / MultiPolygon as JSONB, nullable. NULL is
  a sector that has never been drawn, which stays valid: the name-only bucket
  predates the map and must keep working untouched.
* ``area_ha`` / ``perimeter_m`` — DOUBLE PRECISION, nullable. Derived from
  ``geometry`` and written by the API on every geometry change, never by the
  client (a client-computed area would drift from the stored shape).
* ``color``       — VARCHAR(9), nullable. ``#RRGGBB`` / ``#RRGGBBAA``; the
  per-sector map colour the front already keeps in its local feature
  properties, moved server-side with the shape it belongs to.
* ``geometry_updated_at`` — TIMESTAMPTZ, nullable. When the shape last changed,
  which is NOT when the row last changed (renaming a sector must not look like
  a re-draw to the satellite-statistics recompute that will consume this).

**JSONB, not PostGIS.** PostGIS is not enabled on either Supabase project, and
enabling an extension is a production-affecting change that deserves its own
decision rather than riding along with a feature. GeoJSON in JSONB covers what
the map needs today (round-trip the shape, compute area/perimeter/centroid in
Python). The upgrade path is intact: a later migration can add a ``geography``
column and backfill it from this JSONB without the API contract changing, since
the API speaks GeoJSON either way.

Idempotent DDL so it is safe to re-run against a partially-provisioned DB.

Revision ID: b8c2f0d5e713
Revises: d4e9f1a2b3c8
Create Date: 2026-08-06 20:15:00.000000+00:00
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op


revision: str = "b8c2f0d5e713"
down_revision: Union[str, None] = "d4e9f1a2b3c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE analytics_sector
            ADD COLUMN IF NOT EXISTS geometry            JSONB,
            ADD COLUMN IF NOT EXISTS area_ha             DOUBLE PRECISION,
            ADD COLUMN IF NOT EXISTS perimeter_m         DOUBLE PRECISION,
            ADD COLUMN IF NOT EXISTS color               VARCHAR(9),
            ADD COLUMN IF NOT EXISTS geometry_updated_at TIMESTAMPTZ
        """
    )

    # Partial index: the map's "sectors of this farm that have a shape" read.
    # Only drawn sectors are ever fetched for rendering, and on a farm mid-setup
    # most rows are still name-only, so indexing the NULLs would be dead weight.
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS analytics_sector_user_id_drawn
            ON analytics_sector (user_id)
            WHERE geometry IS NOT NULL
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS analytics_sector_user_id_drawn")
    op.execute(
        """
        ALTER TABLE analytics_sector
            DROP COLUMN IF EXISTS geometry_updated_at,
            DROP COLUMN IF EXISTS color,
            DROP COLUMN IF EXISTS perimeter_m,
            DROP COLUMN IF EXISTS area_ha,
            DROP COLUMN IF EXISTS geometry
        """
    )

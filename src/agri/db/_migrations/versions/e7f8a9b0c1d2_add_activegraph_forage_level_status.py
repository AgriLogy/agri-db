"""add analytics_activegraph.forage_level_status

The borehole (forage) feature (agri-api a1cf719) added a per-user
``forage_level_status`` toggle to Django's ``ActiveGraph`` (Django migration
0069), but the schema-of-record never got the column. Schemas built from
agri-db therefore lack it, Django ActiveGraph queries fail on them, and
fastapp (which reads through agri.db) cannot serve the toggle — agri-api's
active-graph parity tests have failed on main since.

Default TRUE, matching the Django field (``default=True``): the forage section
is shown unless the user turns it off. Idempotent DDL.

Revision ID: e7f8a9b0c1d2
Revises: c9e1a2b3d4f5
Create Date: 2026-11-05 00:00:00.000000+00:00
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op


revision: str = "e7f8a9b0c1d2"
down_revision: Union[str, None] = "c9e1a2b3d4f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE analytics_activegraph "
        "ADD COLUMN IF NOT EXISTS forage_level_status BOOLEAN NOT NULL DEFAULT TRUE"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE analytics_activegraph DROP COLUMN IF EXISTS forage_level_status"
    )

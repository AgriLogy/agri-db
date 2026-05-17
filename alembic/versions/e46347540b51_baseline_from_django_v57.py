"""baseline_from_django_v57

Captures the schema as it stood at the end of the Django era (57+
migrations across CustomUser, agriBack, analytics, django_celery_beat).
Sourced from `pg_dump --schema-only --schema=public` against the
freshly-bootstrapped Supabase dev project.

For an empty Supabase project, `alembic upgrade head` lays the whole
schema down from this single migration. For a project that was already
bootstrapped by Django, run `alembic stamp head` once instead, then
all subsequent migrations apply normally.

Revision ID: e46347540b51
Revises:
Create Date: 2026-05-17 01:39:08.742287+00:00
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence, Union

from alembic import op


revision: str = "e46347540b51"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_BASELINE_SQL = Path(__file__).parent / "0001_baseline.sql"


def upgrade() -> None:
    op.execute(_BASELINE_SQL.read_text())


def downgrade() -> None:
    # Baseline is destructive to reverse — wipe and recreate the public schema.
    op.execute("DROP SCHEMA public CASCADE;")
    op.execute("CREATE SCHEMA public;")
    op.execute("GRANT ALL ON SCHEMA public TO postgres;")
    op.execute("GRANT ALL ON SCHEMA public TO public;")

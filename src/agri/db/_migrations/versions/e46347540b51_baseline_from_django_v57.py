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
    # The pg_dump preamble runs `set_config('search_path', '', false)`, which
    # blanks the search_path for the rest of the transaction. Alembic then
    # writes its version row with an UNQUALIFIED `INSERT INTO alembic_version`,
    # which fails ("relation does not exist") because the table lives in
    # `public` but `public` is no longer on the path. Restore it so the version
    # bookkeeping — and every later migration in this run — resolves. Without
    # this, `alembic upgrade head` from an empty DB has never completed.
    op.execute("SET search_path TO public;")


def downgrade() -> None:
    # Baseline is destructive to reverse — wipe and recreate the public schema.
    op.execute("DROP SCHEMA public CASCADE;")
    op.execute("CREATE SCHEMA public;")
    op.execute("GRANT ALL ON SCHEMA public TO postgres;")
    op.execute("GRANT ALL ON SCHEMA public TO public;")
    # The CASCADE above also dropped `alembic_version`. Alembic finishes a
    # downgrade by DELETE-ing the version row, which would fail on the missing
    # table. Recreate it (with the row this downgrade is about to clear) so the
    # bookkeeping resolves and the DB lands cleanly at base.
    op.execute(
        "CREATE TABLE alembic_version ("
        "version_num VARCHAR(32) NOT NULL, "
        "CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num));"
    )
    op.execute("INSERT INTO alembic_version (version_num) VALUES ('e46347540b51');")

"""add CustomUser_customuser.access_level RBAC column

Three-tier role for user-management RBAC (agri-db #71):

  * ``monitor`` — read-only.
  * ``editor``  — create/edit own data (+ monitor). The default.
  * ``admin``   — user management + delete (+ editor).

The allowed set is validated in the app layer (plain VARCHAR, like the
``preferred_language`` column), not a DB CHECK/enum — matching the house
style for constrained string columns.

Backfill of existing rows (stated here, applied non-destructively below):
  * ``is_staff = true``  -> ``admin``
  * everyone else        -> ``editor``

Every existing account can already edit its own data today, so the fallback
is ``editor`` (not ``monitor``); defaulting to ``monitor`` would silently
remove access those users already have.

Idempotent by construction. The column is added *without* a server default
first, so pre-existing rows land as NULL and the backfill can see them; the
backfill only touches rows whose ``access_level`` is NULL or not one of the
three valid values; the ``'editor'`` server default (for future inserts) and
``NOT NULL`` are set last. Re-running the migration, or running it after a
partial apply, is a no-op on already-classified rows and never clobbers a
value an admin has since changed (``ADD COLUMN IF NOT EXISTS`` skips the
re-add; the guarded ``UPDATE`` matches nothing; ``SET DEFAULT`` / ``SET NOT
NULL`` are harmless when already in effect).

Revision ID: c5d6e7f8a9b0
Revises: f4b6d2e8c1a9
Create Date: 2026-07-23 12:00:00.000000+00:00
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op


revision: str = "c5d6e7f8a9b0"
down_revision: Union[str, None] = "f4b6d2e8c1a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add the column WITHOUT a default so existing rows are NULL and the
    #    backfill below can classify them (a default here would pre-fill every
    #    row with 'editor', hiding is_staff accounts from the promotion).
    op.execute(
        'ALTER TABLE "CustomUser_customuser" '
        "ADD COLUMN IF NOT EXISTS access_level VARCHAR(16)"
    )
    # 2. Backfill only rows not yet holding a valid tier, so a re-run (or a run
    #    after a partial apply where an admin already changed some rows) is a
    #    no-op on already-classified accounts.
    op.execute(
        """
        UPDATE "CustomUser_customuser"
           SET access_level = CASE WHEN is_staff THEN 'admin' ELSE 'editor' END
         WHERE access_level IS NULL
            OR access_level NOT IN ('admin', 'editor', 'monitor')
        """
    )
    # 3. Now that every row has a value, add the default (for future inserts)
    #    and enforce NOT NULL. Both are idempotent to re-assert.
    op.execute(
        'ALTER TABLE "CustomUser_customuser" '
        "ALTER COLUMN access_level SET DEFAULT 'editor'"
    )
    op.execute(
        'ALTER TABLE "CustomUser_customuser" ALTER COLUMN access_level SET NOT NULL'
    )


def downgrade() -> None:
    op.execute('ALTER TABLE "CustomUser_customuser" DROP COLUMN IF EXISTS access_level')

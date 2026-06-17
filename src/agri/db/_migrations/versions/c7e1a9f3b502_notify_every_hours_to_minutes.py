"""notify_every: reinterpret hours -> minutes (backfill x60)

``CustomUser_customuser.notify_every`` previously stored the periodic-email
cadence in *hours*; it now stores *minutes* so sub-hour cadences (e.g. every
10 min) are expressible (see agri-api ``should_notify`` and the agri-admin
minutes UI).

Backfill preserves each user's effective cadence by scaling existing values
x60 (4 h -> 240 min), clamped to the new admin ceiling (10080 min = 7 days,
also keeps the value within ``smallint``). ``notify_every = 0`` ("notify
every tick") is left untouched. Also sets the column default to 240.

Revision ID: c7e1a9f3b502
Revises: b7f2a4c1d9e3
Create Date: 2026-06-17 00:00:00.000000+00:00
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op


revision: str = "c7e1a9f3b502"
down_revision: Union[str, None] = "b7f2a4c1d9e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        'UPDATE "CustomUser_customuser" '
        "SET notify_every = LEAST(notify_every * 60, 10080) "
        "WHERE notify_every > 0"
    )
    op.execute(
        'ALTER TABLE "CustomUser_customuser" '
        "ALTER COLUMN notify_every SET DEFAULT 240"
    )


def downgrade() -> None:
    op.execute(
        'ALTER TABLE "CustomUser_customuser" '
        "ALTER COLUMN notify_every SET DEFAULT 4"
    )
    op.execute(
        'UPDATE "CustomUser_customuser" '
        "SET notify_every = GREATEST(notify_every / 60, 1) "
        "WHERE notify_every > 0"
    )

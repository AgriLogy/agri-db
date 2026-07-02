"""add CustomUser_customuser.sessions_revoked_at

Admin session kill switch. Any JWT (access or refresh) whose ``iat`` is
older than this timestamp is rejected by agri-api, forcing the user to log
out. NULL means the user's sessions have never been revoked.

Mirrors the Django field ``users.0008_customuser_sessions_revoked_at`` and
the SQLAlchemy column on ``CustomUserCustomuser``.

Idempotent ``IF NOT EXISTS`` so re-running on an already-caught-up DB is a
no-op.

Revision ID: a1b2c3d4e5f6
Revises: 31d37a9a428c
Create Date: 2026-06-21 00:00:00.000000+00:00
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "31d37a9a428c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        'ALTER TABLE "CustomUser_customuser" '
        "ADD COLUMN IF NOT EXISTS sessions_revoked_at TIMESTAMPTZ NULL"
    )


def downgrade() -> None:
    op.execute(
        'ALTER TABLE "CustomUser_customuser" DROP COLUMN IF EXISTS sessions_revoked_at'
    )

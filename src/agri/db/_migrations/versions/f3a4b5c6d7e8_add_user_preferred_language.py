"""add CustomUser_customuser.preferred_language column

Per-user preferred language for outbound notifications (agri-api #31): the
periodic field-status email is rendered in French or Arabic based on this.
Mirrors the Django ``CustomUser.preferred_language`` field. Idempotent
``IF NOT EXISTS`` so re-running after a Django ``migrate`` is a no-op.

Revision ID: f3a4b5c6d7e8
Revises: e2f3a4b5c6d7
Create Date: 2026-06-25 21:00:00.000000+00:00
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op


revision: str = "f3a4b5c6d7e8"
down_revision: Union[str, None] = "e2f3a4b5c6d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE \"CustomUser_customuser\" "
        "ADD COLUMN IF NOT EXISTS preferred_language VARCHAR(8) NOT NULL DEFAULT 'fr'"
    )


def downgrade() -> None:
    op.execute(
        'ALTER TABLE "CustomUser_customuser" DROP COLUMN IF EXISTS preferred_language'
    )

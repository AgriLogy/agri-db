"""add alert last_emailed_at column

Mirrors the Django migration ``analytics.0059_alert_last_emailed_at``
(generated 2026-05-20). The column was already declared on the Django
model + the agri-db SQLAlchemy mirror but never landed in the dev
Postgres schema, which made ``Alert.objects.filter(...)`` queries 500
with ``column analytics_alert.last_emailed_at does not exist``.

Idempotent ``IF NOT EXISTS`` so re-running on a DB that has already
caught up via ``manage.py migrate`` is a no-op.

Revision ID: 31d37a9a428c
Revises: e46347540b51
Create Date: 2026-05-28 18:16:13.545105+00:00
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op


revision: str = "31d37a9a428c"
down_revision: Union[str, None] = "e46347540b51"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE analytics_alert "
        "ADD COLUMN IF NOT EXISTS last_emailed_at TIMESTAMPTZ NULL"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE analytics_alert DROP COLUMN IF EXISTS last_emailed_at")

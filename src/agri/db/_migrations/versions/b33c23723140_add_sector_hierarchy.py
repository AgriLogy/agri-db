"""add sector hierarchy

Revision ID: b33c23723140
Revises: b2c3d4e5f6a7
Create Date: 2026-07-20 23:23:12.545769+00:00

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b33c23723140"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # "Sector" grouping: User → Sector → Zone (organizational only, no
    # geometry). See agri.db.analytics.AnalyticsSector.
    op.create_table(
        "analytics_sector",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["CustomUser_customuser.id"],
            name="analytics_sector_user_id_fk_CustomUser_customuser_id",
            deferrable=True,
            initially="DEFERRED",
        ),
        sa.PrimaryKeyConstraint("id", name="analytics_sector_pkey"),
    )
    op.create_index("analytics_sector_user_id", "analytics_sector", ["user_id"])

    # Zones reference their sector; nullable so every existing zone stays
    # "unassigned" (no backfill needed, no downtime).
    op.add_column(
        "analytics_zone", sa.Column("sector_id", sa.BigInteger(), nullable=True)
    )
    op.create_foreign_key(
        "analytics_zone_sector_id_fk_analytics_sector_id",
        "analytics_zone",
        "analytics_sector",
        ["sector_id"],
        ["id"],
        ondelete="SET NULL",
        deferrable=True,
        initially="DEFERRED",
    )
    op.create_index("analytics_zone_sector_id", "analytics_zone", ["sector_id"])


def downgrade() -> None:
    op.drop_index("analytics_zone_sector_id", table_name="analytics_zone")
    op.drop_constraint(
        "analytics_zone_sector_id_fk_analytics_sector_id",
        "analytics_zone",
        type_="foreignkey",
    )
    op.drop_column("analytics_zone", "sector_id")
    op.drop_index("analytics_sector_user_id", table_name="analytics_sector")
    op.drop_table("analytics_sector")

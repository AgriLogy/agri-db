"""add analytics_devicesensor (router sensor attachments)

Revision ID: 00a3976cb808
Revises: c9d0e1f2a3b4
Create Date: 2026-06-28 13:07:05.421369+00:00

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '00a3976cb808'
down_revision: Union[str, None] = 'c9d0e1f2a3b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Sensor attachments for registered routers/gateways: maps a device's wire
    # tag (e.g. a Bivocom Modbus tag) to a sensor_key + farm zone. device_id is a
    # SOFT FK — analytics_device is a Django-managed table, not mirrored here, so
    # no DB-level constraint (matching how Device's own FKs are declared).
    op.create_table(
        "analytics_devicesensor",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("device_id", sa.BigInteger(), nullable=False),
        sa.Column("tag_name", sa.String(length=64), nullable=False),
        sa.Column("sensor_key", sa.String(length=64), nullable=False),
        sa.Column(
            "is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.Column("zone_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["zone_id"],
            ["analytics_zone.id"],
            name="analytics_devicesensor_zone_id_fk",
            ondelete="SET NULL",
            deferrable=True,
            initially="DEFERRED",
        ),
        sa.PrimaryKeyConstraint("id", name="analytics_devicesensor_pkey"),
        sa.UniqueConstraint(
            "device_id", "tag_name", name="analytics_devicesensor_device_tag_uniq"
        ),
    )
    op.create_index(
        "analytics_devicesensor_device_idx", "analytics_devicesensor", ["device_id"]
    )
    op.create_index(
        "analytics_devicesensor_zone_idx", "analytics_devicesensor", ["zone_id"]
    )


def downgrade() -> None:
    op.drop_index("analytics_devicesensor_zone_idx", table_name="analytics_devicesensor")
    op.drop_index(
        "analytics_devicesensor_device_idx", table_name="analytics_devicesensor"
    )
    op.drop_table("analytics_devicesensor")

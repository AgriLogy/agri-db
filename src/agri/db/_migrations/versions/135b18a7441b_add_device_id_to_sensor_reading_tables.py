"""add device_id to sensor reading tables

Revision ID: 135b18a7441b
Revises: e5f6a7b8c9d0
Create Date: 2026-07-12 15:02:18.022887+00:00

Adds a nullable ``device_id`` (soft FK to ``analytics_device.id``, no DB-level
constraint — matches the Django ``db_constraint=False`` convention) plus a
``device_id`` index to every sensor-reading table. Purely additive: nothing reads
or writes the column yet (that lands in later agri-api / agri-core phases), so
this migration is safe to apply on its own and fully reversible.

Ownership of a device-sourced reading will be resolved by JOINing to
``analytics_device``, making a device transfer a single-row update.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "135b18a7441b"
down_revision: Union[str, None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# The 37 sensor-reading tables (every ``analytics_*`` table carrying a reading
# ``value``). Ownership/registry tables (analytics_device, _zone, _alert, …) and
# config tables (analytics_kcperiod) are intentionally excluded.
_READING_TABLES: tuple[str, ...] = (
    "analytics_ecsalinitysensor",
    "analytics_ecsoilhigh",
    "analytics_ecsoillow",
    "analytics_ecsoilmedium",
    "analytics_electricityconsumptionsensor",
    "analytics_et0calculated",
    "analytics_et0weather",
    "analytics_fruitsizesensor",
    "analytics_humidityweather",
    "analytics_largefruitdiametersensor",
    "analytics_leafmoisturesensor",
    "analytics_leaftemperaturesensor",
    "analytics_multidepthsoilmoisturesensor",
    "analytics_npksensor",
    "analytics_phsoil",
    "analytics_phwatersensor",
    "analytics_precipitationrate",
    "analytics_pressureweather",
    "analytics_soilconductivitysensor",
    "analytics_soilmoisturehigh",
    "analytics_soilmoisturelow",
    "analytics_soilmoisturemedium",
    "analytics_soilsalinitysensor",
    "analytics_soiltemperaturehigh",
    "analytics_soiltemperaturelow",
    "analytics_soiltemperaturemedium",
    "analytics_solarradiation",
    "analytics_temperatureweather",
    "analytics_vpdweather",
    "analytics_waterecsensor",
    "analytics_waterflowsensor",
    "analytics_waterlevelsensor",
    "analytics_waterpressuresensor",
    "analytics_winddirection",
    "analytics_windspeed",
    "analytics_batterysensor",
    "analytics_signalsensor",
)


def upgrade() -> None:
    for table in _READING_TABLES:
        op.add_column(table, sa.Column("device_id", sa.BigInteger(), nullable=True))
        # Index name mirrors SQLAlchemy's default for ``mapped_column(index=True)``
        # on the HasDeviceId mixin (ix_<table>_device_id) so ORM↔DB stay drift-free.
        op.create_index(
            op.f(f"ix_{table}_device_id"), table, ["device_id"], unique=False
        )


def downgrade() -> None:
    for table in _READING_TABLES:
        op.drop_index(op.f(f"ix_{table}_device_id"), table_name=table)
        op.drop_column(table, "device_id")

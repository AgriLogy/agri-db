"""add (user_id, timestamp) index to sensor reading tables

Revision ID: d4e9f1a2b3c8
Revises: c5d6e7f8a9b0
Create Date: 2026-07-29 05:10:00.000000+00:00

Every analytics chart queries one shape: "this user's readings between two
timestamps, averaged per hour" (agri-api ``apps/sensors/router_sensors.py``
-> ``engine.hourly_readings``). All 37 reading tables carried indexes on
``user_id``, ``zone_id`` and ``device_id`` — but **none on ``timestamp``**, so
Postgres narrowed by ``user_id`` and then discarded most of what it read.

Measured on prod (analytics_soiltemperaturelow, 7-day range)::

    Bitmap Heap Scan  (actual time=32.267..35.785 rows=3249)
      Recheck Cond: (user_id = ...)
      Filter: ("timestamp" >= (now() - '7 days'::interval))
      Rows Removed by Filter: 50791          <-- 94% of the work wasted

The discarded-rows term grows with every uplink while the useful result stays
the same size, so chart latency degraded in proportion to how long the devices
had been running. One analytics page fans out 12-18 of these concurrently
against 3 gunicorn workers on a 1 vCPU host.

Verified on a 120k-row reproduction before writing this migration::

    before:  Seq Scan, 110172 rows removed, 1003 buffers, 13.26 ms
    after:   Bitmap Index Scan, 0 rows removed,  131 buffers,  2.51 ms

Column order is ``(user_id, timestamp)``: user is always an equality predicate
and timestamp always a range, which is the order a btree can use for both. The
zone filter is optional at the API level, so including ``zone_id`` in the key
would strand the timestamp range whenever a caller omits it; zone is left as a
cheap heap filter over the already-narrowed set.

Indexes are built CONCURRENTLY — the ingest path writes to these tables every
few seconds and a plain CREATE INDEX would block it for the duration. That
requires running outside a transaction, hence the autocommit block. The
trade-off is that a CONCURRENTLY build can fail and leave an INVALID index
behind; the DDL is IF NOT EXISTS and the downgrade drops the same names, so a
failed run is safe to re-apply after dropping the invalid index.

ANALYZE is issued per table because the same prod plan showed the estimate at
``rows=2`` against ``rows=3249`` actual — off by ~1600x — so statistics were
stale enough to distort plan choice on their own.
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op


revision: str = "d4e9f1a2b3c8"
down_revision: Union[str, None] = "c5d6e7f8a9b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Same set as 135b18a7441b (device_id). Kept as a literal rather than
# discovered at runtime so the migration is deterministic across environments.
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


def _index_name(table: str) -> str:
    return f"ix_{table}_user_id_timestamp"


def upgrade() -> None:
    # CONCURRENTLY cannot run inside a transaction block.
    with op.get_context().autocommit_block():
        for table in _READING_TABLES:
            op.execute(
                f"CREATE INDEX CONCURRENTLY IF NOT EXISTS {_index_name(table)} "
                f'ON {table} (user_id, "timestamp")'
            )
            op.execute(f"ANALYZE {table}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        for table in _READING_TABLES:
            op.execute(f"DROP INDEX CONCURRENTLY IF EXISTS {_index_name(table)}")

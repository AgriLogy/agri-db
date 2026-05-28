"""agri.db — the Agrilogy schema-of-record.

Future per-domain modules (users, sensors, irrigation, alerts, devices, ...)
will be added in Phase 4b+ and re-exported here so Alembic autogenerate
sees the full ``AgriBase.metadata``.

This package ships its own Alembic configuration under
``agri.db._migrations``. Downstream consumers (agri-api today; future
ingest service tomorrow) run migrations via the ``agri-migrate``
console script entry point.
"""
from __future__ import annotations

from agri.db.base import AgriBase  # noqa: F401

# Per-domain modules will be re-exported here as Phase 4b+ lands:
# from agri.db.users import *      # noqa: F401, F403
# from agri.db.sensors import *    # noqa: F401, F403
# from agri.db.irrigation import * # noqa: F401, F403

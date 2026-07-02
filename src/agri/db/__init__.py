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

from agri.db._version import __version__  # noqa: F401
from agri.db.base import AgriBase  # noqa: F401

# Per-domain modules — each re-export registers tables on AgriBase.metadata.
# CRITICAL: forgetting a re-export here makes Alembic autogenerate emit
# DROP TABLE for any tables that domain owns. Always add a new domain
# module to this list AND verify `make check-dev` stays clean.
from agri.db.users import *  # noqa: F401, F403
from agri.db.analytics import *  # noqa: F401, F403  (Phase 4c — 47 tables)
from agri.db.feedback import *  # noqa: F401, F403  (in-app bug reports)

# Absorbed from agri-api's ensure_*_tables.py boot scripts (15 tables).
from agri.db.assistant import *  # noqa: F401, F403  (assistant chat history)
from agri.db.audit import *  # noqa: F401, F403  (audit/monitoring/settings)
from agri.db.billing import *  # noqa: F401, F403  (plans/subscriptions/invoices)
from agri.db.devices import *  # noqa: F401, F403  (device registry)
from agri.db.irrigation import *  # noqa: F401, F403  (programs/output commands)
from agri.db.technicians import *  # noqa: F401, F403  (technician RBAC grants)

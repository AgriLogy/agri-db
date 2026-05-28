"""Alembic environment.

Resolves the target database from `DATABASE_URL` (env var or .env). No
credentials live in alembic.ini.

Schema strategy (as of Phase 4a):
  * Baseline migration is a raw-SQL dump captured from the
    Django-bootstrapped schema (e46347…_baseline_from_django_v57.py).
  * SQLAlchemy ORM models will be introduced per-domain in Phase 4b+
    (users, sensors, irrigation, alerts, devices, ...). When that
    starts, flip `target_metadata` to `AgriBase.metadata` and import
    every domain module from `agri.db.__init__` so autogenerate sees
    the full schema.
  * Until then, `target_metadata = None` → autogenerate is disabled;
    all migrations use `op.execute(...)`.
"""

from __future__ import annotations

import os
from collections.abc import MutableMapping
from logging.config import fileConfig
from typing import Literal

from alembic import context
from dotenv import find_dotenv, load_dotenv
from sqlalchemy import create_engine, pool

# Importing agri.db re-exports every domain module → registers all
# tables on AgriBase.metadata. Autogenerate then sees the full schema.
import agri.db  # noqa: F401  (side-effect import — registers tables)
from agri.db.base import AgriBase

# usecwd=True lets us find .env.dev / .env.prod when invoked from
# the repo root (the Makefile targets) regardless of installed location.
load_dotenv(find_dotenv(usecwd=True))

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Source .env.dev or .env.prod (or pass "
        "DATABASE_URL=... inline) before running alembic."
    )

# Note: we do NOT push DATABASE_URL into alembic.ini via
# `config.set_main_option` because configparser interprets `%` as
# interpolation syntax, which breaks any percent-encoded password.
# Instead, create the engine directly from the env var.

target_metadata = AgriBase.metadata


# ---------------------------------------------------------------------------
# Filter Django-managed tables out of autogenerate.
# ---------------------------------------------------------------------------
# These tables live in the DB but should NOT participate in autogenerate
# either because they're managed externally (django_*, auth_*,
# alembic_version) or because they're scheduled for a later phase
# (analytics_* → modeled progressively in Phase 4c-4f).
#
# As each 4c-4f PR mirrors a slice of analytics_* into its own domain
# module, the corresponding tables are REMOVED from this filter — at
# the end of Phase 4f the filter shrinks back to just django_/auth_/
# alembic_version.

_FILTERED_TABLE_PREFIXES = (
    "django_",
    "auth_",
    "analytics_",  # TODO: remove progressively as Phase 4c-4f domain modules land
)
_FILTERED_TABLE_EXACT = {"alembic_version"}

ObjectType = Literal[
    "schema",
    "table",
    "column",
    "index",
    "unique_constraint",
    "foreign_key_constraint",
]


def include_name(
    name: str | None,
    type_: ObjectType,
    parent_names: MutableMapping[str, str | None],
) -> bool:
    """Return False for objects we don't own → autogenerate skips them."""
    if type_ == "table" and name is not None:
        if name in _FILTERED_TABLE_EXACT:
            return False
        if any(name.startswith(p) for p in _FILTERED_TABLE_PREFIXES):
            return False
    return True


def include_object(
    object_: object,
    name: str | None,
    type_: str,
    reflected: bool,
    compare_to: object | None,
) -> bool:
    """Belt-and-braces filter mirroring include_name (which only fires on
    reflected items). Skips Django-managed tables on the metadata side too."""
    if type_ == "table":
        if name in _FILTERED_TABLE_EXACT:
            return False
        if name and any(name.startswith(p) for p in _FILTERED_TABLE_PREFIXES):
            return False
    return True


def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_name=include_name,
        include_object=include_object,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_name=include_name,
            include_object=include_object,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

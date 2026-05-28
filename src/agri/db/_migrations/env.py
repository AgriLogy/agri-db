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
from logging.config import fileConfig

from alembic import context
from dotenv import find_dotenv, load_dotenv
from sqlalchemy import create_engine, pool

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

# No declarative metadata yet — Phase 4b will flip this to
# `AgriBase.metadata` once the first domain module ships.
target_metadata = None


def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

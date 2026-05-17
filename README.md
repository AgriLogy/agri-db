# agrilogy-db

Schema-of-record for the Agrilogy Supabase Postgres. **All schema
changes for both the (legacy) Django backend and the (planned) FastAPI
backend land here, not in app repos.**

Migrations are run with [Alembic](https://alembic.sqlalchemy.org/) over
SQLAlchemy 2.x. The repo is intentionally framework-agnostic — it
contains no ORM models, just raw-SQL migrations via `op.execute(...)`.
Models can be added later when FastAPI lands.

## Baseline

Revision `0001_baseline_from_django_v57` is the schema as it stood at
the end of the Django era (~57 migrations across CustomUser, agriBack,
analytics). It was captured with `pg_dump --schema-only` from the
freshly-bootstrapped Supabase dev project on 2026-05-17.

## Setup

```bash
uv sync
cp .env.example .env.dev    # paste the Supabase DEV Session-pooler URI
cp .env.example .env.prod   # paste the Supabase PROD Session-pooler URI
```

Both `.env.dev` and `.env.prod` are gitignored.

## Daily flow

```bash
make new MSG="add irrigation_log table"     # generates alembic/versions/<rev>_add_irrigation_log_table.py
# edit the file, fill in op.execute("CREATE TABLE ...") / op.create_table(...) etc.

make upgrade-dev      # apply against Supabase dev (sanity-check)
# review the change in Supabase Studio
make upgrade-prod     # promote to Supabase prod
```

## First-time setup of a fresh Supabase project

```bash
# .env.dev or .env.prod must point at the new project
make upgrade-dev      # lays down the entire schema from migration 0001 onward
```

## Stamping an existing database

When a Supabase project already has the schema (e.g. dev was bootstrapped
by Django before we owned migrations), run `make stamp-dev-head` once
instead of `upgrade-dev` — it writes the alembic_version row without
re-running any DDL.

## Connection URI format

Use the **Session pooler** from Supabase Studio → Connect → Session pooler.
The URI looks like:

```
postgresql+psycopg://postgres.<project-ref>:<password>@aws-1-eu-central-1.pooler.supabase.com:5432/postgres
```

The `+psycopg` driver hint tells SQLAlchemy 2.x to use psycopg 3. **Do
not use the Direct connection** (`db.<ref>.supabase.co`) — it is
IPv6-only on the free tier and unreachable from most dev machines.

## Why a separate repo

- Decouples schema lifecycle from app code so a future FastAPI rewrite
  doesn't have to re-do migrations.
- Lets CI / on-call review schema PRs independently of app PRs.
- Eliminates the risk of two apps (Django today, FastAPI tomorrow)
  fighting over a shared migration table.

# Contributing to agri-db

## What this repo is

`agri-db` is the **schema-of-record for the whole Agrilogy platform**. Every table and
column exists here twice, and nowhere else:

1. **SQLAlchemy 2.0 models** in `src/agri/db/*.py` (per-domain modules, all re-exported
   from `agri.db.__init__` so `AgriBase.metadata` sees the full schema), and
2. **Alembic migrations** in `src/agri/db/_migrations/versions/`.

Topology: `agri-api` (HTTP shell) → `agri-core` (logic + DB access) → `agri-db` (this repo).

**Nothing else may own schema.** Django's `manage.py migrate` is OFF in agri-api's
container boot; the legacy `ensure_*_tables.py` boot scripts are being retired (their
15 tables were absorbed here in `e5f6a7b8c9d0`). If you need a column, it lands here first.

> `README.md` is stale on two points: models *do* exist now (it predates Phase 4b), and
> migrations live under `src/agri/db/_migrations/versions/`, not `alembic/`.

## Prerequisites

| Tool | Why |
| --- | --- |
| `uv` | the only package manager used (`uv sync`, `uv run`) |
| Python ≥ 3.12 | `requires-python` in `pyproject.toml` |
| Docker | `make migrate-test` spins a throwaway `postgres:17` |
| `pre-commit` | ruff + Conventional-Commit + pre-push gates |

## First-time setup

```bash
uv sync                       # or: make install
pre-commit install --install-hooks       # pre-commit + commit-msg stages
pre-commit install --hook-type pre-push  # ruff / ORM-configures / release-config gate
```

Environment files (all gitignored except the `*-example` ones):

```bash
cp .env.example      .env.dev    # Supabase DEV Session-pooler URI
cp .env.test-example .env.test   # Supabase agrilogy-test Session-pooler URI
cp .env.example      .env.prod   # prod URI — see "prod caveat" below
```

Only `DATABASE_URL` is read (resolved in `env.py`, never from `alembic.ini`). Use the
Supabase **Session pooler** URI with the `postgresql+psycopg://` scheme — the Direct
connection (`db.<ref>.supabase.co`) is IPv6-only and unreachable from most machines.

There is **no local-Postgres bring-up target** beyond the throwaway one that
`make migrate-test` / `scripts/migrate_test.sh` creates (`postgres:17` on port
`${MIGRATE_TEST_PORT:-55432}`, container `agri-db-migtest`, force-removed on exit).

## Dev loop

All Make targets wrap `uv run alembic -c src/agri/db/_migrations/alembic.ini` and source
the matching `.env.*` so you can't point a command at the wrong database.

| Command | What it does |
| --- | --- |
| `make install` | `uv sync` |
| `make new MSG="add foo table"` | `alembic revision -m "..."` (empty skeleton) |
| `make migrate-test` | **the gate** — empty Docker PG: upgrade head → downgrade base → upgrade head → `alembic check` |
| `make upgrade-test` / `-dev` / `-prod` | `alembic upgrade head` against that env |
| `make current-test` / `-dev` / `-prod` | `alembic current` |
| `make history-dev` / `-prod` | `alembic history --verbose` |
| `make check-test` / `check-dev` | `alembic check` (ORM ↔ DB drift) |
| `make stamp-dev-head` / `stamp-prod-head` | write `alembic_version` without running DDL |

Raw alembic, when a Make target doesn't exist (e.g. `heads`, `downgrade -1`, autogenerate):

```bash
set -a && source .env.test && set +a
uv run alembic -c src/agri/db/_migrations/alembic.ini heads
uv run alembic -c src/agri/db/_migrations/alembic.ini revision --autogenerate -m "add foo"
uv run alembic -c src/agri/db/_migrations/alembic.ini downgrade -1
```

Lint (what CI runs) — there is **no pytest suite in this repo**; the migration harness is
the test suite:

```bash
uv run ruff check .
uv run ruff format --check .
uv run python -c "import agri.db; from sqlalchemy.orm import configure_mappers; configure_mappers()"
```

## Repo layout

| Path | Contents |
| --- | --- |
| `src/agri/db/base.py` | `AgriBase` declarative base + `HasDeviceId` mixin |
| `src/agri/db/__init__.py` | re-exports every domain module — **a missing re-export makes autogenerate emit `DROP TABLE`** |
| `src/agri/db/{users,analytics,devices,irrigation,billing,audit,technicians,assistant,feedback}.py` | per-domain ORM models |
| `src/agri/db/_version.py` | `__version__`, written by semantic-release — never hand-edit |
| `src/agri/db/_migrations/env.py` | Alembic env: `DATABASE_URL`, `target_metadata = AgriBase.metadata`, `django_*`/`auth_*`/`alembic_version` autogenerate filters |
| `src/agri/db/_migrations/alembic.ini` | bundled config (`script_location = %(here)s`, UTC, `%(rev)s_%(slug)s`) |
| `src/agri/db/_migrations/cli.py` | `agri-migrate` console script = `alembic upgrade head`, plus pass-through |
| `src/agri/db/_migrations/versions/` | the revision chain + `0001_baseline.sql` (pg_dump of the Django-era schema) |
| `scripts/migrate_test.sh` | the empty-DB round-trip harness behind `make migrate-test` |
| `.github/workflows/` | thin callers into `AgriLogy/shared-workflows@v1` (+ self-contained `drift-check.yml`) |

## Worked example — adding a column

1. **Edit the model.** e.g. add to `src/agri/db/devices.py` (or a new module — if new,
   add `from agri.db.newmod import *` to `src/agri/db/__init__.py`).

2. **Find the single head, then create the revision.**

   ```bash
   set -a && source .env.test && set +a
   uv run alembic -c src/agri/db/_migrations/alembic.ini heads      # must print ONE head
   make new MSG="add device gps coordinates"
   ```

   Autogenerate (`revision --autogenerate`) is available and metadata-driven, but the
   house style in `versions/` is hand-written `op.execute(...)` with `IF NOT EXISTS` /
   `IF EXISTS` — see `b2c3d4e5f6a7_add_device_gps_coordinates.py` as the template.

3. **Review the generated SQL by hand.** Autogenerate does not know about server
   defaults you didn't declare, index names Django chose, or data backfills. Check
   `down_revision` points at the head from step 2, and write a real `downgrade()` — the
   gate round-trips it.

4. **Test up AND down.**

   ```bash
   make migrate-test          # upgrade → downgrade base → upgrade → alembic check
   ```

5. **Sanity-check against a real DB (optional but preferred).**

   ```bash
   make upgrade-dev && make check-dev
   ```

6. **Downstream pick-up** — release order matters:
   - `agri-db` merges → `release.yml` tags a new bare `{version}`.
   - `agri-core` bumps `"agri-db @ git+https://github.com/AgriLogy/agri-db.git@<tag>"`
     in its `pyproject.toml`, `uv lock`, releases.
   - `agri-api` bumps its `agri-core` pin in `back/pyproject.toml`, `uv lock`, deploys.

## Non-negotiable migration rules

- **One PR = one revision**, chained on the current single head. **No forks.** The chain
  already forked once off `31d37a9a428c` and needed the merge revision
  `d1e2f3a4b5c6_add_zone_elevation_merge_heads.py` to heal — don't repeat it. Run
  `alembic heads` before you write `down_revision`.
- **Model and migration land together.** A model without its migration turns the nightly
  `drift-check.yml` red.
- **Review autogenerated diffs by hand** — never merge raw autogenerate output.
- **Every migration needs a working `downgrade()`.** `make migrate-test` runs
  `downgrade base` and will fail on orphaned objects.
- **Prefer idempotent DDL** (`ADD COLUMN IF NOT EXISTS`, `DROP ... IF EXISTS`) — some
  tables were created out-of-band on the droplet by the legacy ensure-scripts.
- **`search_path` gotcha (baseline).** `0001_baseline.sql` carries the pg_dump preamble
  `set_config('search_path', '', false)`, which blanks the path for the rest of the
  transaction and breaks Alembic's unqualified `INSERT INTO alembic_version`. The
  baseline revision restores it with `SET search_path TO public;`. Any future raw-dump
  migration must do the same.
- **Migrations are applied to production BEFORE deploying an agri-api that expects
  them.** The reverse order is an outage. Prod cutover runbook:
  **`agri-api/docs/MIGRATIONS_PROD_CUTOVER.md`**.

## Environments

| GitHub Environment | Database | `DATABASE_URL` secret | Applied by |
| --- | --- | --- | --- |
| `test` | Supabase `agrilogy-test` | set | `apply-test.yml` — automatic on merge to main |
| `dev` | Supabase dev | set | `apply-dev.yml` dispatch (`dry_run=true` first), or `make upgrade-dev` |
| `prod` | droplet `agrydata` container | **not set** | manual only |

**Prod caveat.** `apply-prod.yml` exists but is not operational: the `prod` environment
has no `DATABASE_URL` secret, and prod predates the Alembic baseline. The one-time stamp
cutover in `agri-api/docs/MIGRATIONS_PROD_CUTOVER.md` must run before the first real
`upgrade head` there — otherwise `upgrade head` replays the baseline onto populated
tables. Stamping an already-schema'd database is `make stamp-prod-head` (writes
`alembic_version`, runs no DDL). Some migrations are deliberately **held** pending that
cutover; check the runbook and the paired issue before assuming a revision is live.

## Release / versioning

python-semantic-release, driven by Conventional Commits on `main` (`release.yml`):
computes the next version, rewrites `src/agri/db/_version.py`, updates `CHANGELOG.md`,
tags **bare `{version}`** (no `v` prefix — agri-core pins by git tag), and cuts a GitHub
Release. `feat` → minor, `fix`/`perf` → patch, `major_on_zero = false`. `feat|fix|perf/*`
branches can cut an `rc` prerelease via `workflow_dispatch`. Release order is always
**agri-db → agri-core → agri-api**.

## Branch + PR rules

- Branch off `main` (`feat/…`, `fix/…`, `ci/…`).
- **Conventional Commit PR titles are enforced** (`lint-pr-title.yml`) — squash-merge
  uses the PR title as the release input. Commit messages are enforced locally too by
  `conventional-pre-commit --strict`.
- **One dedicated, scope-matched issue per PR**, with `Closes #N` in the body.
- Issue and PR are both assigned to the author, `mks-zakaria` (`auto-assign.yml` does it).
- **Zero AI/assistant attribution anywhere** — no `Co-Authored-By`, no bot identity, in
  commits, PR bodies, issues or branch names. Commit from your local machine only.

## CI

| Workflow | Trigger | What runs | Reproduce locally |
| --- | --- | --- | --- |
| `primary.yml` (CI) | PR, push to main | `shared-workflows/python-lint.yml@v1` — ruff check + format check | `uv run ruff check . && uv run ruff format --check .` |
| `migrations.yml` | PR, push to main | `shared-workflows/migrations-gate.yml@v1` — empty DB upgrade → downgrade → upgrade + `alembic check` | `make migrate-test` |
| `lint-pr-title.yml` | PR opened/edited/synced | Conventional-Commit title check | — |
| `apply-test.yml` | push to main touching `versions/**` | `alembic upgrade head` on the `test` DB | `make upgrade-test` |
| `apply-dev.yml` / `apply-prod.yml` | manual dispatch | render SQL (`dry_run=true`) or apply | `make upgrade-dev` / `make upgrade-prod` |
| `drift-check.yml` | nightly 03:00 UTC + dispatch | `alembic current` + `alembic check` on `test` and `dev`, fails on drift | `make check-test`, `make check-dev` |
| `release.yml` | push to main (skips `[skip ci]`) | semantic-release | — |
| `auto-assign.yml` | issue/PR opened | assigns `mks-zakaria` | — |

All logic lives in `AgriLogy/shared-workflows@v1`; the files here own only triggers,
concurrency and inputs. `drift-check.yml` is the one self-contained workflow. CI pins
uv `0.11.6` (`uv.lock` is revision 3 and needs a modern uv).

## Gotchas

- **Missing re-export = data loss.** Forgetting a domain module in
  `src/agri/db/__init__.py` makes autogenerate emit `DROP TABLE` for its tables.
- **`alembic check` in `make migrate-test` is informational, not fatal** — a known
  FK-naming drift on `analytics_alert` predates the harness. In `drift-check.yml` it *is*
  fatal, so don't add new drift.
- **agri-db is a PRIVATE repo.** Downstream installs (`agri-core`, agri-api CI/Docker)
  need a read-only PAT exposed as **`AGRI_DB_RO_TOKEN`**, configured as a git credential
  so `uv sync` can fetch `git+https://github.com/AgriLogy/agri-db.git@<tag>`. For local
  co-development against an unreleased agri-db, use `uv pip install -e ../agri-db`.
- **Bootstrap order:** apply this repo's schema (`make upgrade-dev`) *before* filling
  agri-api's `back/.env` and running `make up` there.
- **`agri-migrate`** is the console script downstream services call
  (`agri-migrate` = `upgrade head`; extra argv is forwarded to alembic). In agri-api it
  is gated behind `RUN_DB_MIGRATIONS`, which ships OFF.

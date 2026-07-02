# agri-db onboarding

## What this repo is

**The schema-of-record for the Agrilogy Postgres.** In the backend topology

```
agri-api  (Django/ninja HTTP shell)
   └── agri-core  (business logic + handlers, SQLAlchemy DB access)
          └── agri-db  (THIS REPO — ORM models + Alembic migration history)
```

every table and column the platform uses is declared here, twice:

1. **SQLAlchemy 2.0 models** under `src/agri/db/` (per-domain modules —
   `users`, `analytics`, `billing`, `devices`, `irrigation`, `audit`,
   `technicians`, `assistant`, `feedback` — all re-exported in
   `agri.db.__init__` so `AgriBase.metadata` sees the full schema), and
2. **Alembic migrations** under `src/agri/db/_migrations/versions/`.

Nothing else is allowed to change the database: Django's `manage.py migrate`
is OFF in agri-api's container boot, and the legacy `ensure_*_tables.py` boot
scripts are being retired now that their tables are absorbed here.

## Bootstrap order

Apply this repo's schema **before** starting the consumers:

```
agri-db `make upgrade-dev`  →  fill agri-api back/.env  →  agri-api `make up`
```

## Migration workflow

```
make new MSG="add analytics_foo table"     # writes a new revision skeleton
# edit the revision + the matching ORM model (keep them in sync!)
make migrate-test                          # empty-Docker-Postgres gate (local)
# open a PR  →  CI runs:
#   - migrations (migrations-gate.yml@v1): empty DB upgrade → downgrade →
#     upgrade round-trip + informational `alembic check`
#   - CI lint (python-lint.yml@v1): ruff check + ruff format --check
#   - Lint PR title: Conventional-Commit title (squash commit = release input)
# merge to main  →
#   - apply-test.yml AUTO-APPLIES `alembic upgrade head` to the TEST database
#   - release.yml cuts a semantic-release version
# then promote by hand, in order:
#   - dev:  dispatch apply-dev.yml  (dry_run=true first, then false)
#           — or locally: make upgrade-dev
#   - prod: see "prod caveat" below
# nightly: drift-check.yml runs `alembic current` + `alembic check` against
#          test + dev and FAILS on ORM <-> DB drift
```

Rules of thumb:

* One PR = one revision; chain on the current single head
  (`uv run alembic -c src/agri/db/_migrations/alembic.ini heads`).
* Model change and migration land together, else the nightly drift check
  turns red.
* Prefer idempotent DDL (`IF NOT EXISTS`) when a table may already exist
  out-of-band (droplet legacy).
* Every migration needs a working `downgrade()` — the gate round-trips it.

## Environments

| GitHub Environment | Database | `DATABASE_URL` secret | Applied by |
| --- | --- | --- | --- |
| `test` | Supabase **agrilogy-test** (`bsphfxmkjjurahpytznm`, eu-central-1) | ✅ set | `apply-test.yml` — automatic on merge to main |
| `dev`  | Supabase dev (`rkctyieaptkuezbylhws`) | ✅ set | `apply-dev.yml` dispatch, or `make upgrade-dev` |
| `prod` | Droplet `agrydata` container (live) | ❌ **not set** | manual only — see caveat |

Local equivalents live in gitignored `.env.test` / `.env.dev` / `.env.prod`
(see `.env.example` + `.env.test-example`); the Make targets
(`upgrade-test|dev|prod`, `current-*`, `check-*`) source them.

**Prod caveat:** `apply-prod.yml` exists but is not operational — the `prod`
environment has no `DATABASE_URL` secret yet, and prod predates the Alembic
baseline, so the one-time stamp cutover in
`agri-api/docs/MIGRATIONS_PROD_CUTOVER.md` must run before the first real
`upgrade head` there.

## CI is shared

All workflow logic lives in **AgriLogy/shared-workflows** (pinned `@v1`);
this repo's `.github/workflows/*.yml` are thin callers that only own the
triggers, concurrency groups and inputs. Exception: `drift-check.yml` is
self-contained (no shared drift workflow yet — upstream candidate).

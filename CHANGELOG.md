# CHANGELOG


## v0.10.0 (2026-06-25)

### Features

- **activegraph**: Add water_level_status visibility flag
  ([#40](https://github.com/AgriLogy/agri-db/pull/40),
  [`28b0341`](https://github.com/AgriLogy/agri-db/commit/28b0341faf6372b0113567f305a92217a2043759))

Per-zone toggle for the water-level dashboard section (agrilogy-front #4 follow-up), mirroring the
  existing *_status flags on analytics_activegraph. Migration b8c9d0e1f2a3 (idempotent) off head
  a7b8c9d0e1f2; mirror updated.


## v0.9.0 (2026-06-25)

### Features

- **alert**: Add grace_override_seconds column ([#38](https://github.com/AgriLogy/agri-db/pull/38),
  [`6f9b297`](https://github.com/AgriLogy/agri-db/commit/6f9b297321755754896d912d873271cae349a107))

Per-alert grace override (agri-api #37): an optional per-alert re-notify cadence that beats the
  global ALERT_GRACE_PERIODS[sensor_key] when set. Migration a7b8c9d0e1f2 (idempotent) off head
  f3a4b5c6d7e8; mirror updated.


## v0.8.0 (2026-06-25)

### Features

- **users**: Add preferred_language column ([#36](https://github.com/AgriLogy/agri-db/pull/36),
  [`ddc922d`](https://github.com/AgriLogy/agri-db/commit/ddc922d8188a98265c0a1f5abc9f59e83d1348c4))

Per-user notification language (agri-api #31). Migration f3a4b5c6d7e8 (idempotent ADD COLUMN IF NOT
  EXISTS preferred_language VARCHAR(8) NOT NULL DEFAULT 'fr', revises head e2f3a4b5c6d7) on
  CustomUser_customuser; mirror updated. Mirrors the Django CustomUser.preferred_language field.


## v0.7.0 (2026-06-25)

### Features

- **notifications**: Custom notification zones + alert notify_sms
  ([#34](https://github.com/AgriLogy/agri-db/pull/34),
  [`c4b044a`](https://github.com/AgriLogy/agri-db/commit/c4b044adb513ee829d98ec66c697e4b65e665c84))

Custom notification zones (agrilogy-front #57): analytics_notificationzone (user-owned alert
  grouping, independent of farm analytics_zone) + analytics_notificationzonesensor (sensor_key +
  source_zone_id stream), plus analytics_alert.notification_zone_id (alert binds to a farm zone XOR
  a notification zone) and analytics_alert.notify_sms. Migration e2f3a4b5c6d7 (idempotent) revises
  head d1e2f3a4b5c6; SQLAlchemy mirrors added.


## v0.6.0 (2026-06-25)

### Features

- **zone**: Add elevation_m + merge divergent alembic heads
  ([#32](https://github.com/AgriLogy/agri-db/pull/32),
  [`3bd8d9b`](https://github.com/AgriLogy/agri-db/commit/3bd8d9b5e6eb421e90aae51591fe39bb1e3678b0))

Adds analytics_zone.elevation_m (DOUBLE, default 0, metres) so the agronomy clear-sky radiation Rso
  = (0.75 + 2e-5*elevation_m)*Ra is correct away from sea level. AnalyticsZone SQLAlchemy mirror
  updated.

Migration d1e2f3a4b5c6 also merges the three heads that had diverged off 31d37a9a428c
  (sessions_revoked_at / notify channels / notify-minutes) so 'alembic upgrade head' resolves to one
  head again.

Supports agri-api #15.


## v0.5.0 (2026-06-25)

### Features

- **alert**: Add notify_email + notify_whatsapp columns
  ([#30](https://github.com/AgriLogy/agri-db/pull/30),
  [`519b475`](https://github.com/AgriLogy/agri-db/commit/519b475b6c7033f1ddf9e69c632e1c1447e00664))

Per-alert delivery channels. Alembic migration c4d8e1f02a37 (idempotent ADD COLUMN IF NOT EXISTS,
  revises head 31d37a9a428c) adds notify_email BOOLEAN NOT NULL DEFAULT TRUE + notify_whatsapp
  BOOLEAN NOT NULL DEFAULT FALSE to analytics_alert. AnalyticsAlert SQLAlchemy mirror updated (+ the
  missing last_emailed_at to cut drift). Mirrors Django analytics.0061.

Closes #20


## v0.4.0 (2026-06-21)

### Chores

- **ci**: Auto-assign new issues and PRs to mks-zakaria
  ([#25](https://github.com/AgriLogy/agri-db/pull/25),
  [`0d34274`](https://github.com/AgriLogy/agri-db/commit/0d342748338c5e8641c477362e211bddd2e80636))

### Continuous Integration

- Fix Auto Assign workflow failing on pull_request events
  ([#27](https://github.com/AgriLogy/agri-db/pull/27),
  [`fc38563`](https://github.com/AgriLogy/agri-db/commit/fc38563420d67b06e229300a008e32f43ff2f1ed))

Replace pozil/auto-assign-issue@v1 (which errors with "Couldn't find issue info in current context"
  on pull_request, and warns on the invalid numOfAssignee input) with a single gh-api call to the
  issues/assignees endpoint, which assigns both issues and PRs since a PR shares its repo's
  issue-number space.

### Features

- Add CustomUser.sessions_revoked_at session kill switch
  ([`edc2ede`](https://github.com/AgriLogy/agri-db/commit/edc2edef7fa03cd7ae628ba26012d64a54768653))

New nullable TIMESTAMPTZ column backing the admin force-logout / disable feature. Any JWT whose iat
  predates this timestamp is rejected by agri-api, forcing the user to log out. Adds the SQLAlchemy
  column + an idempotent Alembic migration mirrored by the Django field.


## v0.3.0 (2026-06-17)

### Features

- **users**: Notify_every hours->minutes backfill (x60) + default 240
  ([#23](https://github.com/AgriLogy/agri-db/pull/23),
  [`cb2c06a`](https://github.com/AgriLogy/agri-db/commit/cb2c06ab4b8bdbc6d5d9f681c74e1996bab9a869))

Migration c7e1a9f3b502 (down_revision b7f2a4c1d9e3): scale existing notify_every values x60
  (4h->240min, clamped to 10080), set column default 240. SQLAlchemy model server_default aligned.
  Pairs with agri-api minutes cadence + agri-admin minutes UI; apply this FIRST in the deploy order.


## v0.2.0 (2026-06-07)

### Features

- **analytics**: Add battery + signal sensor tables
  ([#19](https://github.com/AgriLogy/agri-db/pull/19),
  [`68eae48`](https://github.com/AgriLogy/agri-db/commit/68eae480cc2af8b087406dc134b338bc26caf8b7))

Two new per-zone device-health metrics, same shape as every analytics sensor table (id, timestamp,
  user_id, zone_id, value): * analytics_batterysensor — battery voltage (V), from LoRaWAN nodes *
  analytics_signalsensor — RSSI (dBm), from LoRaWAN nodes + Bivocom

SQLAlchemy mirrors + an idempotent Alembic migration. Lets agri-core's db_model_for resolve the new
  'battery'/'signal' registry keys.


## v0.1.1 (2026-05-29)

### Bug Fixes

- **deps**: Drop unused pydantic dependency ([#17](https://github.com/AgriLogy/agri-db/pull/17),
  [`ba35a74`](https://github.com/AgriLogy/agri-db/commit/ba35a74b5c4ed6fe9acab17cfb925ca80f7ed376))

Closes #16


## v0.1.0 (2026-05-29)

### Bug Fixes

- **model**: Add missing user-side reverse relationships
  ([#13](https://github.com/AgriLogy/agri-db/pull/13),
  [`06cf9d0`](https://github.com/AgriLogy/agri-db/commit/06cf9d0b1ba77651d4b9256311bafc199667b5b1))

Every analytics model declares a user-side relationship (user/decided_by/requested_by) with
  back_populates naming an attribute on CustomUserCustomuser, but the hand-curated users.py only
  ever defined a couple of them. SQLAlchemy pairs back_populates by (target class, property name),
  so the missing reverse properties made configure_mappers() raise for the whole registry on the
  first ORM operation -- meaning any query through agri.core.database would fail.

Add the 45 reverse relationships (44 single-FK + the two-FK ManagerAffirmation pair, which name
  their foreign_keys) so mappers configure cleanly. Guard the cross-module class names with a
  TYPE_CHECKING import (runtime-free; resolved via the shared AgriBase registry). Drop the
  now-unused MetaData import.

Verified: configure_mappers() succeeds (50 mappers) and a real query executes against an in-memory
  SQLite build of the schema subset.

- **release**: Build_command must be a string; use empty string to skip
  ([`d02f87f`](https://github.com/AgriLogy/agri-db/commit/d02f87f09a20dcb14e7479b08ec586eb2615513b))

- **release**: Skip build step; agri-db is consumed by git tag, not a wheel
  ([`549b3af`](https://github.com/AgriLogy/agri-db/commit/549b3af6274488f60eb826b23bc2874f4b2ce17f))

The PSR action runs in its own container without uv on PATH, so build_command='uv build' failed
  (127). agri-db needs no built artifact (consumers pin it by git tag), so set build_command=false.

### Chores

- Apply claude-token-optimizer + initial CLAUDE.md
  ([#11](https://github.com/AgriLogy/agri-db/pull/11),
  [`638f712`](https://github.com/AgriLogy/agri-db/commit/638f7125b4767901178cbbd2deb3a4240f485989))

This repo had no CLAUDE.md. Run cto init to bootstrap the optimized doc structure, then replace the
  autodetected (and incorrect) "django application" Project Overview with one that actually
  describes agri-db: the Supabase Postgres schema-of-record owned by Alembic + SQLAlchemy.

Adds: - CLAUDE.md (sibling-repos table, Read-First warnings, quick commands). - .claudeignore
  (excludes README.md / CHANGELOG.md etc. from auto-load). -
  .claude/{COMMON_MISTAKES,QUICK_START,ARCHITECTURE_MAP}.md skeletons + docs/INDEX.md.

- Rename agrilogy-db → agri-db ([#2](https://github.com/AgriLogy/agri-db/pull/2),
  [`8461dc0`](https://github.com/AgriLogy/agri-db/commit/8461dc0e369797bcfbd8ad912e89733da8b495dc))

Phase 0b of the senior-dev refactor (5-repo agri-* ecosystem). Repo rename only; package
  restructuring deferred to Phase 4.

- README.md heading - pyproject.toml name = "agri-db" - uv.lock refreshed

Issue: AgriLogy/agrilogy-db#1

Tracker: AgriLogy/agrilogy-back#48

- Trigger initial semantic-release run
  ([`498e6b4`](https://github.com/AgriLogy/agri-db/commit/498e6b422ef454ec43ecbf3a1fda84cb7b60a9f2))

- **release**: Adopt python-semantic-release ([#15](https://github.com/AgriLogy/agri-db/pull/15),
  [`d665dd5`](https://github.com/AgriLogy/agri-db/commit/d665dd5a83a683dd36736669b9a5f1e2ad277260))

* chore(release): adopt python-semantic-release

First step of the tag-pinned dependency topology (full Revly): give agri-db real
  versions/tags/releases so agri-core can pin `agri-db @ git+…@<tag>` instead of a path dep.

- src/agri/db/_version.py owns __version__ (re-exported as agri.db.__version__); pyproject version
  becomes dynamic, sourced from it. - [tool.semantic_release]: conventional commits → bump + bare
  {version} tag + GitHub release + CHANGELOG. Bare tag (not v-prefixed) because agri-db is consumed
  by tagged URL, matching data-model/revly-core. - .github/workflows/release.yml: manual-dispatch
  release, git identity pinned to mks-zakaria (no bot author). - .pre-commit-config.yaml:
  conventional-pre-commit (commit-msg) + ruff.

Schema unchanged; no Alembic migration.

* ci(release): auto-release on push to main

Trigger semantic-release on push to main (not just manual dispatch) so merging a feat/fix auto-cuts
  a release. The pushed release commit carries [skip ci], so it does not loop.

### Features

- Scaffold agrilogy-db with Alembic and baseline_from_django_v57
  ([`0c94172`](https://github.com/AgriLogy/agri-db/commit/0c9417238b1ec6adb50a4347ebae5a9eead234d7))

Schema-of-record for the Agrilogy Supabase Postgres. Captures the schema as it stood at the end of
  the Django era (~57 migrations) via pg_dump --schema-only into the baseline revision e46347540b51.

All future schema changes for both the (legacy) Django backend and the (planned) FastAPI backend
  land here. Dev was bootstrapped by Django one last time, then stamped at the baseline so this repo
  owns it from now on.

Tooling: SQLAlchemy 2.x, psycopg 3, Alembic 1.18, managed by uv.

- **migrations**: Add analytics_alert.last_emailed_at column
  ([#10](https://github.com/AgriLogy/agri-db/pull/10),
  [`ffad80c`](https://github.com/AgriLogy/agri-db/commit/ffad80cb8be0722c2ff1b882049cc36d545524f0))

Mirror of Django migration analytics.0059_alert_last_emailed_at. The column was on the Django model
  + the agri-db SQLAlchemy mirror but had never landed in the dev Postgres, so
  Alert.objects.filter(...) was 500-ing with "column analytics_alert.last_emailed_at does not
  exist".

Idempotent ALTER TABLE / DROP COLUMN with IF (NOT) EXISTS so re-running on a DB that has caught up
  via manage.py migrate is a no-op.

Verified: make upgrade-dev ran cleanly (e46347540b51 -> 31d37a9a428c) and /api/alert/ +
  /api/alerts/for-graph/ now return 200.

- **model**: Bootstrap src/agri/db/ package + bundled Alembic + agri-migrate CLI
  ([#4](https://github.com/AgriLogy/agri-db/pull/4),
  [`071e78f`](https://github.com/AgriLogy/agri-db/commit/071e78fe87472e2e8c99490e4f0a01f5425ac327))

Phase 4a of the senior-dev refactor. Structural move only; SQLAlchemy ORM models per domain come in
  Phase 4b+.

Layout change: alembic/ → src/agri/db/_migrations/ alembic.ini → src/agri/db/_migrations/alembic.ini
  (new) src/agri/db/__init__.py namespace + future re-exports (new) src/agri/db/base.py AgriBase
  (SQLAlchemy 2.0 DeclarativeBase + to_dict / __repr__ helpers) (new)
  src/agri/db/_migrations/__init__.py (new) src/agri/db/_migrations/cli.py → `agri-migrate` console
  script

pyproject.toml: - src/ layout (package-dir = src) - [project.scripts] agri-migrate =
  "agri.db._migrations.cli:main" - [tool.setuptools.package-data] bundles alembic.ini + versions/*
  in the wheel so downstream services don't need to checkout the source

alembic.ini: - script_location + prepend_sys_path use %(here)s so the bundled config works whether
  run from source or installed wheel

env.py: - target_metadata stays None for now (autogenerate disabled until Phase 4b adds the first
  domain's ORM models) - find_dotenv(usecwd=True) so .env.dev/.env.prod work from the Makefile
  targets at the repo root

Makefile: - $(ALEMBIC) = uv run alembic -c $(ALEMBIC_INI) → all targets use the bundled config
  without env-var dance - new check-dev target (alembic check against dev)

Verified: - uv sync builds the package as editable - agri-migrate --help shows the alembic
  pass-through - alembic -c src/agri/db/_migrations/alembic.ini --help works

Issue: AgriLogy/agri-db#3

Tracker: AgriLogy/agrilogy-back#48

- **model**: Mirror all 47 analytics_* tables; full schema drift-free
  ([#8](https://github.com/AgriLogy/agri-db/pull/8),
  [`b17e575`](https://github.com/AgriLogy/agri-db/commit/b17e575c0715a95e7736e1bfd950aa95445fad58))

Phase 4c — combined with Phase 4b, agri-db now models every app-owned table from the live Supabase
  schema.

- src/agri/db/analytics.py: 1100+ lines, 47 model classes covering zones/locations, agronomy
  (ET0/Kc), every sensor reading table (air/soil/water/leaf/fruit/energy), alerts/notifications, UI
  prefs. Generated from live Supabase via sqlacodegen, adapted to AgriBase and SQLAlchemy 2.0. -
  src/agri/db/__init__.py: re-export agri.db.analytics - _migrations/env.py: removed 'analytics_'
  from filter (now modeled)

Verified: make check-dev → 'No new upgrade operations detected.' All 50 app-owned tables in
  AgriBase.metadata; 13 Django-managed tables remain filtered.

Issue: AgriLogy/agri-db#7

Tracker: AgriLogy/agrilogy-back#48

- **model**: Mirror users domain (CustomUser + 2 M2M tables) in src/agri/db/users.py
  ([#6](https://github.com/AgriLogy/agri-db/pull/6),
  [`3d7af55`](https://github.com/AgriLogy/agri-db/commit/3d7af5519557167749e2fce8a9d46269dcc46e31))

Phase 4b of the senior-dev refactor. First per-domain SQLAlchemy module; establishes the
  autogenerate-driven workflow for 4c-4f.

src/agri/db/users.py: - CustomUserCustomuser — 16 columns matching live Supabase schema (id,
  password, last_login, is_superuser from Django AbstractBaseUser+ PermissionsMixin; firstname,
  lastname, phone_number, geo coords, notification cadence from the agri-api app code). Index on
  date_joined is DESC (matches Django's `-date_joined` ordering). - CustomUserCustomuserGroups — M2M
  to auth_group - CustomUserCustomuserUserPermissions — M2M to auth_permission - auth_group +
  auth_permission — bare stubs on AgriBase.metadata so SQLAlchemy can resolve the FKs; filtered out
  of autogenerate in env.py

Generated from live Supabase dev via sqlacodegen, then adapted to use AgriBase. SQLAlchemy 2.0
  Mapped[] typing throughout — per user constraint that every Python type is typed.

src/agri/db/__init__.py: - Re-export agri.db.users so Alembic autogenerate sees the tables on
  AgriBase.metadata

src/agri/db/_migrations/env.py: - target_metadata = AgriBase.metadata (flipped from None) -
  include_name + include_object filters skip django_*, auth_*, alembic_version (Django-managed) AND
  analytics_* (Phase 4c-4f). Filters are wired to BOTH offline and online migrations (was
  offline-only). - compare_type=True + compare_server_default=True for tight drift detection

pyproject.toml: - pydantic added to runtime deps (per user constraint; not used in this PR but
  pre-positioned for Phase 4c+ DTO/validator work) - sqlacodegen added to dev deps for future
  per-domain generation passes

Verified: - `make check-dev` (alembic check against Supabase dev) → "No new upgrade operations
  detected." Zero drift.

Out of scope: - Mirroring analytics_* tables (Phase 4c-4f) - pydantic DTOs for the user domain (will
  live in agri-api/back/schemas/)

Issue: AgriLogy/agri-db#5

Tracker: AgriLogy/agrilogy-back#48

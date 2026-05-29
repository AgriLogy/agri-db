# CLAUDE.md

**Quick-start guide for Claude Code - Complete details in linked docs**

---

## Project Overview

Schema-of-record for the Agrilogy Supabase Postgres. Owns the SQLAlchemy
ORM models + the Alembic migration history that every backend service
(`agri-api` today, FastAPI tomorrow) consumes.

**Tech Stack**: Python 3.12 · SQLAlchemy 2.0 · Alembic · psycopg · uv

## Sibling repos

| Repo | Path | Role |
|---|---|---|
| `agri-api` | `../agri-api/` | Django+DRF HTTP service. Imports `agri.db` models; never runs `manage.py migrate`. |
| `agri-core` | `../agri-core/` | Framework-agnostic shared lib. |

## ⚠ Read first

1. **Schema lives here, not in agri-api.** Django's `manage.py migrate` is OFF in
   `agri-api`'s container boot. New columns/tables go through Alembic here.
2. **Bootstrap order:** `make upgrade-dev` here BEFORE `make up` in agri-api.
3. **Two Supabase projects:** dev `rkctyieaptkuezbylhws` (`make upgrade-dev`),
   prod `cnjwixfrexcfwhmwtpot` (`make upgrade-prod`, requires prod password).
4. **Commit rules:** local machine only; no `Co-Authored-By`; every PR pairs
   with an issue; use `mks-zakaria`.

## Quick commands

```bash
make install     # uv sync
make new MSG=... # alembic revision -m "..."
make upgrade-dev # apply pending migrations to Supabase dev
make current-dev # show current head on dev
make check-dev   # alembic check (ORM ↔ DB drift)
```

---

## Session Start Protocol ⚡

**MANDATORY** at start of each session:

```bash
# Load essential docs (~800 tokens - 2 min read)
✓ .claude/COMMON_MISTAKES.md      # ⚠️ CRITICAL - Read FIRST
✓ .claude/QUICK_START.md          # Essential commands
✓ .claude/ARCHITECTURE_MAP.md     # File locations
```

**At task completion:**
- Create completion doc in `.claude/completions/YYYY-MM-DD-task-name.md`
- Move session file to `.claude/sessions/archive/` (if created)

**⚠️ NEVER auto-load:**
- Files in `.claude/completions/` (0 token cost)
- Files in `.claude/sessions/` (0 token cost)
- Files in `docs/archive/` (0 token cost)

---

## Quick Start Commands

```bash
# Add your common commands here
```

---

**Last Updated**: 2026-05-29
**Optimized with**: [Claude Token Optimizer](https://github.com/nadimtuhin/claude-token-optimizer)

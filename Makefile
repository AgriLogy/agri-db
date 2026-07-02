## Convenience wrappers around `alembic`. Each target loads the matching
## .env (dev or prod) so you can't accidentally point one command at the
## wrong database.

ALEMBIC_INI := src/agri/db/_migrations/alembic.ini
ALEMBIC      := uv run alembic -c $(ALEMBIC_INI)

.PHONY: help install new migrate-test upgrade-test current-test check-test \
        upgrade-dev upgrade-prod current-dev current-prod \
        history-dev history-prod stamp-dev-head stamp-prod-head check-dev

help:
	@echo "Targets:"
	@echo "  install         uv sync the repo"
	@echo "  new MSG=...     create a new revision (alembic revision -m '...')"
	@echo "  migrate-test    apply the whole chain to a throwaway empty Postgres"
	@echo "                  in Docker (upgrade + round-trip + drift check)."
	@echo "                  RUN THIS BEFORE PUSHING a migration."
	@echo "  upgrade-test    apply pending migrations to the persistent TEST DB"
	@echo "  current-test    show current head on the TEST DB"
	@echo "  check-test      alembic check against the TEST DB (ORM <-> DB drift)"
	@echo "  upgrade-dev     apply pending migrations to Supabase dev"
	@echo "  upgrade-prod    apply pending migrations to Supabase prod"
	@echo "  current-dev     show current head on dev"
	@echo "  current-prod    show current head on prod"
	@echo "  history-dev     full revision history on dev"
	@echo "  history-prod    full revision history on prod"
	@echo "  stamp-dev-head  mark dev as already at the latest revision (no DDL run)"
	@echo "  stamp-prod-head mark prod as already at the latest revision (no DDL run)"
	@echo "  check-dev       alembic check against dev (ORM ↔ DB drift)"

install:
	uv sync

migrate-test:
	@bash scripts/migrate_test.sh

new:
	@test -n "$(MSG)" || (echo "MSG is required: make new MSG='describe change'"; exit 1)
	$(ALEMBIC) revision -m "$(MSG)"

upgrade-test:
	@set -a && source .env.test && set +a && $(ALEMBIC) upgrade head

current-test:
	@set -a && source .env.test && set +a && $(ALEMBIC) current

check-test:
	@set -a && source .env.test && set +a && $(ALEMBIC) check

upgrade-dev:
	@set -a && source .env.dev && set +a && $(ALEMBIC) upgrade head

upgrade-prod:
	@set -a && source .env.prod && set +a && $(ALEMBIC) upgrade head

current-dev:
	@set -a && source .env.dev && set +a && $(ALEMBIC) current

current-prod:
	@set -a && source .env.prod && set +a && $(ALEMBIC) current

history-dev:
	@set -a && source .env.dev && set +a && $(ALEMBIC) history --verbose

history-prod:
	@set -a && source .env.prod && set +a && $(ALEMBIC) history --verbose

stamp-dev-head:
	@set -a && source .env.dev && set +a && $(ALEMBIC) stamp head

stamp-prod-head:
	@set -a && source .env.prod && set +a && $(ALEMBIC) stamp head

check-dev:
	@set -a && source .env.dev && set +a && $(ALEMBIC) check

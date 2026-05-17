## Convenience wrappers around `alembic`. Each target loads the matching
## .env (dev or prod) so you can't accidentally point one command at the
## wrong database.

.PHONY: help install new upgrade-dev upgrade-prod current-dev current-prod \
        history-dev history-prod stamp-dev-head stamp-prod-head

help:
	@echo "Targets:"
	@echo "  install         uv sync the repo"
	@echo "  new MSG=...     create a new revision (alembic revision -m '...')"
	@echo "  upgrade-dev     apply pending migrations to Supabase dev"
	@echo "  upgrade-prod    apply pending migrations to Supabase prod"
	@echo "  current-dev     show current head on dev"
	@echo "  current-prod    show current head on prod"
	@echo "  history-dev     full revision history on dev"
	@echo "  history-prod    full revision history on prod"
	@echo "  stamp-dev-head  mark dev as already at the latest revision (no DDL run)"
	@echo "  stamp-prod-head mark prod as already at the latest revision (no DDL run)"

install:
	uv sync

new:
	@test -n "$(MSG)" || (echo "MSG is required: make new MSG='describe change'"; exit 1)
	uv run alembic revision -m "$(MSG)"

upgrade-dev:
	@set -a && source .env.dev && set +a && uv run alembic upgrade head

upgrade-prod:
	@set -a && source .env.prod && set +a && uv run alembic upgrade head

current-dev:
	@set -a && source .env.dev && set +a && uv run alembic current

current-prod:
	@set -a && source .env.prod && set +a && uv run alembic current

history-dev:
	@set -a && source .env.dev && set +a && uv run alembic history --verbose

history-prod:
	@set -a && source .env.prod && set +a && uv run alembic history --verbose

stamp-dev-head:
	@set -a && source .env.dev && set +a && uv run alembic stamp head

stamp-prod-head:
	@set -a && source .env.prod && set +a && uv run alembic stamp head

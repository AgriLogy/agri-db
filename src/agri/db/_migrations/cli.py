"""Console-script entry point for ``agri-migrate``.

Equivalent to ``alembic upgrade head`` against the bundled config.
What downstream services (agri-api, future ingest worker) call from
their deploy / CI pipelines.

Usage::

    agri-migrate                # upgrade head against $DATABASE_URL
    agri-migrate downgrade -1   # forwards extra args to alembic

The full alembic CLI is also available via:

    ALEMBIC_CONFIG=$(python -c 'import agri.db._migrations as m; print(m.__path__[0]+"/alembic.ini")') \\
        alembic <args>
"""

from __future__ import annotations

import sys
from pathlib import Path

from alembic.config import main as alembic_main


def _config_path() -> str:
    return str(Path(__file__).parent / "alembic.ini")


def main() -> None:
    """Default behavior: `alembic upgrade head`. Pass-through any extra argv."""
    cfg = _config_path()
    if len(sys.argv) > 1:
        # forward whatever the caller asked for, with our config
        alembic_main(argv=["-c", cfg, *sys.argv[1:]])
    else:
        alembic_main(argv=["-c", cfg, "upgrade", "head"])


if __name__ == "__main__":
    main()

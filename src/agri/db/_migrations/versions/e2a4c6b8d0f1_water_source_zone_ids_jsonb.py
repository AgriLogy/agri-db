"""water_source.zone_ids: bigint[] -> jsonb

d1f3a5b7c9e2 created ``water_source.zone_ids`` as ``BIGINT[]``, the only
Postgres ARRAY column in the schema. Consumers that mirror the schema on
SQLite for tests (agri-api) already map JSONB to JSON but cannot render ARRAY,
so store the list as JSONB like every other list-valued column here. Existing
values are converted with ``to_jsonb``.

Revision ID: e2a4c6b8d0f1
Revises: d1f3a5b7c9e2
Create Date: 2026-11-15 18:00:00.000000+00:00
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "e2a4c6b8d0f1"
down_revision: Union[str, None] = "d1f3a5b7c9e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'water_source' AND column_name = 'zone_ids'
                  AND data_type = 'ARRAY'
            ) THEN
                ALTER TABLE water_source ALTER COLUMN zone_ids DROP DEFAULT;
                ALTER TABLE water_source
                    ALTER COLUMN zone_ids TYPE JSONB USING to_jsonb(zone_ids);
                ALTER TABLE water_source
                    ALTER COLUMN zone_ids SET DEFAULT '[]'::jsonb;
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'water_source' AND column_name = 'zone_ids'
                  AND data_type = 'jsonb'
            ) THEN
                ALTER TABLE water_source ALTER COLUMN zone_ids DROP DEFAULT;
                ALTER TABLE water_source
                    ALTER COLUMN zone_ids TYPE BIGINT[]
                    USING translate(zone_ids::text, '[]', '{}')::bigint[];
                ALTER TABLE water_source
                    ALTER COLUMN zone_ids SET DEFAULT '{}'::bigint[];
            END IF;
        END $$;
        """
    )

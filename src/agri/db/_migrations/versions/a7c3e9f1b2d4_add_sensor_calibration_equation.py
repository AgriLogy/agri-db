"""add equation-based calibration to analytics_sensorcalibration

agri-api #460. The affine ``real = raw * scale_a + offset_b`` cannot express a
real field calibration (quadratic soil-moisture curves, exponential probes,
circular wind-vane offsets). The general form is a user-written equation in
``x`` (the captured value) whose coefficients are fitted from reference points
``(captured, real)`` — the maths lives in ``agri.core.calibration_equation``.

Four nullable / defaulted columns, so every existing row keeps behaving exactly
as before (blank ``equation`` = the affine path):

* ``equation``         — the expression, e.g. ``a*x^2 + b*x + c``; '' = affine;
* ``coefficients``     — JSON object ``{name: value}`` applied with it;
* ``reference_points`` — JSON array of ``{captured, real}`` the fit used, kept
                         so the calibration is traceable and can be re-fitted;
* ``fit_metrics``      — JSON summary of the fit (R², RMSE, max error, ...).

Idempotent DDL.

Revision ID: a7c3e9f1b2d4
Revises: e7f8a9b0c1d2
Create Date: 2026-11-11 00:00:00.000000+00:00
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op


revision: str = "a7c3e9f1b2d4"
down_revision: Union[str, None] = "e7f8a9b0c1d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE analytics_sensorcalibration "
        "ADD COLUMN IF NOT EXISTS equation TEXT NOT NULL DEFAULT ''"
    )
    op.execute(
        "ALTER TABLE analytics_sensorcalibration "
        "ADD COLUMN IF NOT EXISTS coefficients JSONB"
    )
    op.execute(
        "ALTER TABLE analytics_sensorcalibration "
        "ADD COLUMN IF NOT EXISTS reference_points JSONB"
    )
    op.execute(
        "ALTER TABLE analytics_sensorcalibration "
        "ADD COLUMN IF NOT EXISTS fit_metrics JSONB"
    )


def downgrade() -> None:
    for column in ("fit_metrics", "reference_points", "coefficients", "equation"):
        op.execute(
            f"ALTER TABLE analytics_sensorcalibration DROP COLUMN IF EXISTS {column}"
        )

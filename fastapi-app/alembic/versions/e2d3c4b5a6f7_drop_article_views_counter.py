"""Drop the unused article views counter.

Revision ID: e2d3c4b5a6f7
Revises: a146b4399399
Create Date: 2026-10-02
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "e2d3c4b5a6f7"
down_revision: str | Sequence[str] | None = "a146b4399399"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column("articles", "views_counter")


def downgrade() -> None:
    op.add_column(
        "articles",
        sa.Column(
            "views_counter",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )

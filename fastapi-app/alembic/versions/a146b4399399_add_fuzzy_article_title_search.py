"""Add fuzzy article title search.

Revision ID: a146b4399399
Revises: c4e8b2f90a61
Create Date: 2026-10-01 16:14:56.316307

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a146b4399399"
down_revision: str | Sequence[str] | None = "c4e8b2f90a61"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute(
        """
        CREATE INDEX ix_articles_title_trgm
        ON articles USING gin (title gin_trgm_ops)
        """
    )


def downgrade() -> None:
    op.drop_index("ix_articles_title_trgm", table_name="articles")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")

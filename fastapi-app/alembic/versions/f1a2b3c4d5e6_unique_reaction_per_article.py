"""Allow one reaction per user and article.

Revision ID: f1a2b3c4d5e6
Revises: d780e1ec90a1
Create Date: 2026-08-27
"""

from collections.abc import Sequence

from alembic import op

revision: str = "f1a2b3c4d5e6"
down_revision: str | Sequence[str] | None = "d780e1ec90a1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_reactions_user_article",
        "reactions",
        ["user_id", "article_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_reactions_user_article",
        "reactions",
        type_="unique",
    )

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
    # Existing installations may already contain several reactions from the
    # same user for one article. Keep the latest one before adding the
    # constraint, then make the denormalized article counters match the data.
    op.execute(
        """
        WITH ranked_reactions AS (
            SELECT
                id,
                ROW_NUMBER() OVER (
                    PARTITION BY user_id, article_id
                    ORDER BY created_at DESC, id DESC
                ) AS row_number
            FROM reactions
        )
        DELETE FROM reactions
        USING ranked_reactions
        WHERE reactions.id = ranked_reactions.id
          AND ranked_reactions.row_number > 1
        """
    )
    op.execute(
        """
        UPDATE articles AS article
        SET
            "like" = counters.likes,
            dislike = counters.dislikes
        FROM (
            SELECT
                article.id,
                COUNT(reaction.id) FILTER (
                    WHERE reaction.reaction_type = 'like'
                ) AS likes,
                COUNT(reaction.id) FILTER (
                    WHERE reaction.reaction_type = 'dislike'
                ) AS dislikes
            FROM articles AS article
            LEFT JOIN reactions AS reaction
                ON reaction.article_id = article.id
            GROUP BY article.id
        ) AS counters
        WHERE article.id = counters.id
        """
    )
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

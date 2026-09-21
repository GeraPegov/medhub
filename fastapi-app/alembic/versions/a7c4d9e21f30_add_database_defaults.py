"""Add database-side defaults and align the article author foreign key.

Revision ID: a7c4d9e21f30
Revises: bd642ce3ec84
Create Date: 2026-09-20
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "a7c4d9e21f30"
down_revision: str | Sequence[str] | None = "bd642ce3ec84"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "subscriptions",
        existing_type=postgresql.JSONB(),
        existing_nullable=False,
        server_default=sa.text("'[]'::jsonb"),
    )
    op.alter_column(
        "articles",
        "like",
        existing_type=sa.Integer(),
        existing_nullable=False,
        server_default=sa.text("0"),
    )
    op.alter_column(
        "articles",
        "dislike",
        existing_type=sa.Integer(),
        existing_nullable=False,
        server_default=sa.text("0"),
    )
    op.alter_column(
        "articles",
        "views_counter",
        existing_type=sa.Integer(),
        existing_nullable=False,
        server_default=sa.text("0"),
    )
    op.drop_constraint(
        "articles_user_id_fkey",
        "articles",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "articles_user_id_fkey",
        "articles",
        "users",
        ["user_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "articles_user_id_fkey",
        "articles",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "articles_user_id_fkey",
        "articles",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.alter_column(
        "articles",
        "views_counter",
        existing_type=sa.Integer(),
        existing_nullable=False,
        server_default=None,
    )
    op.alter_column(
        "articles",
        "dislike",
        existing_type=sa.Integer(),
        existing_nullable=False,
        server_default=None,
    )
    op.alter_column(
        "articles",
        "like",
        existing_type=sa.Integer(),
        existing_nullable=False,
        server_default=None,
    )
    op.alter_column(
        "users",
        "subscriptions",
        existing_type=postgresql.JSONB(),
        existing_nullable=False,
        server_default=None,
    )

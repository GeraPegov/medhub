"""Limit the admins table to one row.

Revision ID: c4e8b2f90a61
Revises: a7c4d9e21f30
"""

from collections.abc import Sequence

from alembic import op

revision: str = "c4e8b2f90a61"
down_revision: str | Sequence[str] | None = "a7c4d9e21f30"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE UNIQUE INDEX admins_one_row ON admins ((true))")


def downgrade() -> None:
    op.drop_index("admins_one_row", table_name="admins")

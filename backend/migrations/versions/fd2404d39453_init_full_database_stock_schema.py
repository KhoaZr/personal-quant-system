"""init_full_database_stock_schema

Revision ID: fd2404d39453
Revises:
Create Date: 2026-10-05 23:16:54.386077

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "fd2404d39453"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""

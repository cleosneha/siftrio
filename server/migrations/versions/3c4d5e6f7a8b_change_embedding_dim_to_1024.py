"""change embedding dimension to 1024 for mistral-embed

Revision ID: 3c4d5e6f7a8b
Revises: 2a3b4c5d6e7f
Create Date: 2026-06-23 18:00:00.000000
"""
from typing import Sequence, Union

from alembic import op

revision: str = "3c4d5e6f7a8b"
down_revision: Union[str, None] = "2a3b4c5d6e7f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE meeting_chunks ALTER COLUMN embedding TYPE vector(1024) USING embedding::vector(1024)")


def downgrade() -> None:
    op.execute("ALTER TABLE meeting_chunks ALTER COLUMN embedding TYPE vector(1536) USING embedding::vector(1536)")

"""add_fts_indexes

Revision ID: 87a43c1c4aa8
Revises: e5f6a7b8c9d0
Create Date: 2026-07-03 20:34:36.924960
"""
from typing import Sequence, Union

from alembic import op


revision: str = "87a43c1c4aa8"
down_revision: Union[str, None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_meeting_chunks_fts "
        "ON meeting_chunks "
        "USING GIN (to_tsvector('english', chunk_text))"
    )

    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_requirements_fts "
        "ON requirements "
        "USING GIN (to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')))"
    )

    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_action_items_fts "
        "ON action_items "
        "USING GIN (to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')))"
    )

    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_decisions_fts "
        "ON decisions "
        "USING GIN (to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')))"
    )

    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_risks_fts "
        "ON risks "
        "USING GIN (to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')))"
    )

    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_questions_fts "
        "ON questions "
        "USING GIN (to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')))"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_meeting_chunks_fts")
    op.execute("DROP INDEX IF EXISTS idx_requirements_fts")
    op.execute("DROP INDEX IF EXISTS idx_action_items_fts")
    op.execute("DROP INDEX IF EXISTS idx_decisions_fts")
    op.execute("DROP INDEX IF EXISTS idx_risks_fts")
    op.execute("DROP INDEX IF EXISTS idx_questions_fts")

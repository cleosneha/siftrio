"""add HNSW index and promote metadata columns

Revision ID: a1b2c3d4e5f6
Revises: d9aa226fe691
Create Date: 2026-06-29 19:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "d9aa226fe691"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "meeting_chunks",
        sa.Column(
            "workspace_id",
            sa.UUID(),
            sa.ForeignKey("workspaces.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column(
        "meeting_chunks",
        sa.Column(
            "client_id",
            sa.UUID(),
            sa.ForeignKey("clients.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column(
        "meeting_chunks",
        sa.Column(
            "project_id",
            sa.UUID(),
            sa.ForeignKey("projects.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    op.create_index("idx_chunk_workspace_id", "meeting_chunks", ["workspace_id"])
    op.create_index("idx_chunk_client_id", "meeting_chunks", ["client_id"])
    op.create_index("idx_chunk_project_id", "meeting_chunks", ["project_id"])

    op.execute(
        "CREATE INDEX idx_chunk_embedding_hnsw "
        "ON meeting_chunks USING hnsw (embedding vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 200)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_chunk_embedding_hnsw")
    op.drop_index("idx_chunk_project_id", table_name="meeting_chunks")
    op.drop_index("idx_chunk_client_id", table_name="meeting_chunks")
    op.drop_index("idx_chunk_workspace_id", table_name="meeting_chunks")
    op.drop_column("meeting_chunks", "project_id")
    op.drop_column("meeting_chunks", "client_id")
    op.drop_column("meeting_chunks", "workspace_id")

from sqlalchemy import ForeignKey, Index, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from src.models.base import Base, TimestampMixin, UUIDMixin


class MeetingChunk(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "meeting_chunks"

    meeting_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
    )

    workspace_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="SET NULL"),
        nullable=True,
    )

    client_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="SET NULL"),
        nullable=True,
    )

    project_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    chunk_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    embedding: Mapped[list[float]] = mapped_column(
        Vector(1024),
        nullable=False,
    )

    chunk_metadata: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
    )

    meeting = relationship(
        "Meeting",
        back_populates="chunks",
    )

    __table_args__ = (
        Index("idx_chunk_meeting_id", "meeting_id"),
        Index("idx_chunk_workspace_id", "workspace_id"),
        Index("idx_chunk_client_id", "client_id"),
        Index("idx_chunk_project_id", "project_id"),
        Index(
            "idx_chunk_embedding_hnsw",
            embedding,
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 200},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

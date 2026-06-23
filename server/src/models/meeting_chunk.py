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

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    chunk_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    embedding: Mapped[list[float]] = mapped_column(
        Vector(1536),
        nullable=False,
    )

    meeting = relationship(
        "Meeting",
        back_populates="chunks",
    )
    
    chunk_metadata: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    default=dict,
    )

    __table_args__ = (
        Index(
            "idx_chunk_meeting_id",
            "meeting_id",
        ),
    )
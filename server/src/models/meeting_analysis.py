from sqlalchemy import Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class MeetingAnalysis(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "meeting_analysis"

    meeting_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    goal: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    outcomes: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    blockers: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    raw_ai_response: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    meeting = relationship(
        "Meeting",
        back_populates="analysis",
    )

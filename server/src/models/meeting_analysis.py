from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
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

    decisions: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    action_items: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    answered_questions: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    unanswered_questions: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    risks: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    blockers: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    future_meetings: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    generated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    meeting = relationship(
        "Meeting",
        back_populates="analysis",
    )

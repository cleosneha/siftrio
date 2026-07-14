from datetime import date, time
from enum import Enum

from sqlalchemy import Date, Enum as SQLEnum, Float, ForeignKey, String, Text, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class SuggestionStatus(str, Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    DISMISSED = "dismissed"


class MeetingSuggestion(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "meeting_suggestions"

    meeting_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    suggested_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    start_time: Mapped[time | None] = mapped_column(
        Time,
        nullable=True,
    )

    end_time: Mapped[time | None] = mapped_column(
        Time,
        nullable=True,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[SuggestionStatus] = mapped_column(
        SQLEnum(SuggestionStatus),
        nullable=False,
        default=SuggestionStatus.PENDING,
    )

    meeting = relationship(
        "Meeting",
        back_populates="suggestions",
    )

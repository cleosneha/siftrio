from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class MeetingType(str, Enum):
    PROJECT = "project"
    MISCELLANEOUS = "miscellaneous"


class MeetingProvider(str, Enum):
    MANUAL = "manual"
    GOOGLE_MEET = "google_meet"


class TranscriptStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Meeting(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "meetings"

    created_by: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    creator = relationship(
        "User",
        back_populates="created_meetings",
        foreign_keys=[created_by],
    )

    client_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
    )

    project_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    meeting_type: Mapped[MeetingType] = mapped_column(
        SQLEnum(MeetingType),
        default=MeetingType.PROJECT,
        nullable=False,
    )

    tags: Mapped[list[str]] = mapped_column(
        ARRAY(Text),
        nullable=False,
        default=list,
    )

    transcript: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    meeting_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    start_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    meeting_provider: Mapped[MeetingProvider] = mapped_column(
        SQLEnum(MeetingProvider),
        default=MeetingProvider.MANUAL,
        nullable=False,
    )

    meeting_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    google_calendar_event_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    google_meet_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    google_meet_code: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    fireflies_meeting_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    transcript_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    guest_emails: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text),
        nullable=True,
    )

    client = relationship(
        "Client",
        back_populates="meetings",
    )

    project = relationship(
        "Project",
        back_populates="meetings",
    )

    chunks = relationship(
        "MeetingChunk",
        back_populates="meeting",
        cascade="all, delete-orphan",
    )

    analysis = relationship(
        "MeetingAnalysis",
        back_populates="meeting",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_meeting_client_id", "client_id"),
        Index("idx_meeting_project_id", "project_id"),
        Index("idx_meeting_meeting_date", "meeting_date"),
        Index("idx_meeting_google_calendar_event_id", "google_calendar_event_id"),
        Index("idx_meeting_google_meet_code", "google_meet_code"),
        Index("idx_meeting_fireflies_meeting_id", "fireflies_meeting_id"),
    )

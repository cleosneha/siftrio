from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class Meeting(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "meetings"

    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    transcript: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    meeting_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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

    __table_args__ = (
        Index(
            "idx_meeting_project_id",
            "project_id",
        ),
    )
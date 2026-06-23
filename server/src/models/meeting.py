from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class MeetingType(str, Enum):
    PROJECT = "project"
    MISCELLANEOUS = "miscellaneous"


class Meeting(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "meetings"

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

    __table_args__ = (
        Index(
            "idx_meeting_client_id",
            "client_id",
        ),
        Index(
            "idx_meeting_project_id",
            "project_id",
        ),
    )

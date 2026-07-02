from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class RequirementStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"


class ActionItemStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DecisionStatus(str, Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"


class RiskSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskStatus(str, Enum):
    OPEN = "open"
    MITIGATED = "mitigated"
    CLOSED = "closed"


class QuestionStatus(str, Enum):
    ANSWERED = "answered"
    PENDING = "pending"


class AIEntityBase:
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    meeting_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    source_chunk_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meeting_chunks.id", ondelete="SET NULL"),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    @declared_attr
    def meeting(cls):
        return relationship("Meeting")

    @declared_attr
    def project(cls):
        return relationship("Project")


class Requirement(AIEntityBase, Base):
    __tablename__ = "requirements"

    priority: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    approved_by: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class ActionItem(AIEntityBase, Base):
    __tablename__ = "action_items"

    assignee: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )


class Decision(AIEntityBase, Base):
    __tablename__ = "decisions"

    decision_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class Risk(AIEntityBase, Base):
    __tablename__ = "risks"

    severity: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )

    mitigation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


class Question(AIEntityBase, Base):
    __tablename__ = "questions"

    answer: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

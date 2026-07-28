from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from src.models.base import Base, Priority, TimestampMixin, UUIDMixin


class RequirementStatus(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    REJECTED = "rejected"


class ActionItemStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"


class DecisionStatus(str, Enum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class RiskStatus(str, Enum):
    OPEN = "open"
    MITIGATED = "mitigated"
    CLOSED = "closed"
    ACCEPTED = "accepted"


class QuestionStatus(str, Enum):
    OPEN = "open"
    ANSWERED = "answered"
    CLOSED = "closed"


class RiskSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AIEntityBase(UUIDMixin, TimestampMixin):
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

    @declared_attr
    def meeting(cls):
        return relationship("Meeting")

    @declared_attr
    def project(cls):
        return relationship("Project")

    @declared_attr
    def source_chunk(cls):
        return relationship("MeetingChunk")


class Requirement(AIEntityBase, Base):
    __tablename__ = "requirements"

    status: Mapped[RequirementStatus] = mapped_column(
        SQLEnum(RequirementStatus),
        nullable=False,
        default=RequirementStatus.PROPOSED,
        index=True,
    )

    priority: Mapped[Priority | None] = mapped_column(
        SQLEnum(Priority),
        nullable=True,
        index=True,
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

    approver = relationship("User", foreign_keys=[approved_by])

    __table_args__ = (
        Index("idx_requirement_project_status", "project_id", "status"),
        Index("idx_requirement_meeting_status", "meeting_id", "status"),
    )


class ActionItem(AIEntityBase, Base):
    __tablename__ = "action_items"

    status: Mapped[ActionItemStatus] = mapped_column(
        SQLEnum(ActionItemStatus),
        nullable=False,
        default=ActionItemStatus.TODO,
        index=True,
    )

    assignee_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    assignee_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    assignee = relationship("User", foreign_keys=[assignee_id])

    priority: Mapped[Priority | None] = mapped_column(
        SQLEnum(Priority),
        nullable=True,
    )

    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    __table_args__ = (
        Index("idx_action_item_project_status", "project_id", "status"),
        Index("idx_action_item_meeting_status", "meeting_id", "status"),
    )


class Decision(AIEntityBase, Base):
    __tablename__ = "decisions"

    status: Mapped[DecisionStatus] = mapped_column(
        SQLEnum(DecisionStatus),
        nullable=False,
        default=DecisionStatus.PROPOSED,
        index=True,
    )

    decision_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        Index("idx_decision_project_status", "project_id", "status"),
        Index("idx_decision_meeting_status", "meeting_id", "status"),
    )


class Risk(AIEntityBase, Base):
    __tablename__ = "risks"

    status: Mapped[RiskStatus] = mapped_column(
        SQLEnum(RiskStatus),
        nullable=False,
        default=RiskStatus.OPEN,
        index=True,
    )

    severity: Mapped[RiskSeverity | None] = mapped_column(
        SQLEnum(RiskSeverity),
        nullable=True,
        index=True,
    )

    mitigation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    __table_args__ = (
        Index("idx_risk_project_status", "project_id", "status"),
        Index("idx_risk_meeting_status", "meeting_id", "status"),
    )


class Question(AIEntityBase, Base):
    __tablename__ = "questions"

    status: Mapped[QuestionStatus] = mapped_column(
        SQLEnum(QuestionStatus),
        nullable=False,
        default=QuestionStatus.OPEN,
        index=True,
    )

    answer: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    __table_args__ = (
        Index("idx_question_project_status", "project_id", "status"),
        Index("idx_question_meeting_status", "meeting_id", "status"),
    )

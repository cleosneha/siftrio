from enum import Enum

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    created_by: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )

    creator = relationship(
        "User",
        back_populates="created_projects",
        foreign_keys=[created_by],
    )

    client_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(ProjectStatus),
        default=ProjectStatus.ACTIVE,
        nullable=False,
    )

    client = relationship(
        "Client",
        back_populates="projects",
    )

    meetings = relationship(
        "Meeting",
        back_populates="project",
    )

    __table_args__ = (
        Index(
            "idx_project_client_id",
            "client_id",
        ),
    )
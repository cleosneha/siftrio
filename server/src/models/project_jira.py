from sqlalchemy import ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class ProjectJira(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "project_jira"

    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="jira",
    )

    jira_project_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    jira_project_key: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    jira_project_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    jira_project_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    project = relationship(
        "Project",
        back_populates="jira_integration",
    )

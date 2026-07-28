from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class ProjectIntegration(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "project_integrations"
    __table_args__ = (
        UniqueConstraint("project_id", "provider", name="uq_project_integration"),
    )

    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    external_project_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    external_project_key: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    external_project_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    config: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
    )

    project = relationship(
        "Project",
        back_populates="integrations",
    )

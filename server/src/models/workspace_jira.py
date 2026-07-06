from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class WorkspaceJira(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "workspace_jira"

    workspace_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="jira",
    )

    access_token: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    refresh_token: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    cloud_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    cloud_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    site_url: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    connected_by: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    connected_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=True,
    )

    workspace = relationship(
        "Workspace",
        back_populates="jira_integration",
    )

    connector = relationship(
        "User",
        foreign_keys=[connected_by],
    )

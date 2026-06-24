from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class Client(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "clients"

    created_by: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )

    creator = relationship(
        "User",
        back_populates="created_clients",
        foreign_keys=[created_by],
    )

    workspace_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
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

    workspace = relationship(
        "Workspace",
        back_populates="clients",
    )

    projects = relationship(
        "Project",
        back_populates="client",
        cascade="all, delete-orphan",
    )

    meetings = relationship(
        "Meeting",
        back_populates="client",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index(
            "idx_client_workspace_id",
            "workspace_id",
        ),
    )
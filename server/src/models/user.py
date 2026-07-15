from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    full_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    profile_picture: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    google_id: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    integrations = relationship(
        "UserIntegration",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    created_workspaces = relationship(
        "Workspace",
        back_populates="creator",
        foreign_keys="Workspace.created_by",
        cascade="all, delete-orphan",
    )

    created_clients = relationship(
        "Client",
        back_populates="creator",
        foreign_keys="Client.created_by",
        cascade="all, delete-orphan",
    )

    created_projects = relationship(
        "Project",
        back_populates="creator",
        foreign_keys="Project.created_by",
        cascade="all, delete-orphan",
    )

    created_meetings = relationship(
        "Meeting",
        back_populates="creator",
        foreign_keys="Meeting.created_by",
        cascade="all, delete-orphan",
    )

    workspace_memberships = relationship(
        "WorkspaceMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    client_memberships = relationship(
        "ClientMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    project_memberships = relationship(
        "ProjectMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    sent_invitations = relationship(
        "MemberInvitation",
        back_populates="invited_by_user",
        foreign_keys="MemberInvitation.invited_by",
        cascade="all, delete-orphan",
    )

    api_keys = relationship(
        "ApiKey",
        back_populates="user",
        cascade="all, delete-orphan",
    )

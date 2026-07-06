from enum import Enum
from uuid import UUID

from sqlalchemy import Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin
from src.models.workspace_member import MemberRole


class ProjectMember(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "project_members"

    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    role: Mapped[MemberRole] = mapped_column(
        SQLEnum(MemberRole),
        nullable=False,
        default=MemberRole.MEMBER,
    )

    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")

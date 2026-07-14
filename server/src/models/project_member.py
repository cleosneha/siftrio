from enum import Enum
from uuid import UUID

from sqlalchemy import Enum as SQLEnum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin
from src.models.workspace_member import MemberRole


class ProjectMember(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "project_members"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_member_user"),
    )

    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role: Mapped[MemberRole] = mapped_column(
        SQLEnum(MemberRole),
        nullable=False,
        default=MemberRole.MEMBER,
    )

    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")

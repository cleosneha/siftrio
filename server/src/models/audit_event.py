from uuid import UUID

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin, UUIDMixin


class RbacAuditEvent(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "rbac_audit_events"

    workspace_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )

    actor_user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    actor_api_key_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("api_keys.id", ondelete="SET NULL"),
        nullable=True,
    )

    action: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    resource_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    resource_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )

    old_value: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    new_value: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    ip_address: Mapped[str | None] = mapped_column(
        INET,
        nullable=True,
    )

    user_agent: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    __table_args__ = (
        Index("idx_rbac_audit_workspace_created", "workspace_id", "created_at"),
        Index("idx_rbac_audit_user_created", "actor_user_id", "created_at"),
    )

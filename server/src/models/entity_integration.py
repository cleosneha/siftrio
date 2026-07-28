from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum as SQLEnum, ForeignKey, Index, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, SyncStatus, TimestampMixin, UUIDMixin


class EntityIntegration(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "entity_integrations"

    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    entity_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    external_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    external_key: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    external_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    external_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    sync_status: Mapped[SyncStatus | None] = mapped_column(
        SQLEnum(SyncStatus),
        nullable=True,
    )

    synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    external_assignee_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    extra_data: Mapped[dict | None] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
        default=dict,
    )

    __table_args__ = (
        UniqueConstraint("entity_type", "entity_id", "provider", name="uq_entity_integration"),
        Index("idx_entity_integration_entity", "entity_type", "entity_id"),
        CheckConstraint(
            "entity_type IN ('action_item', 'requirement', 'decision', 'risk', 'question')",
            name="chk_entity_type",
        ),
    )

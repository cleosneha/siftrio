from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class UserIntegration(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "user_integrations"

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
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

    scopes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="integrations",
    )

"""add users and user_integrations tables

Revision ID: 5e6f7a8b9c0d
Revises: 4d5e6f7a8b9c
Create Date: 2026-06-24 10:49:27.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "5e6f7a8b9c0d"
down_revision: Union[str, None] = "4d5e6f7a8b9c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("profile_picture", sa.Text(), nullable=True),
        sa.Column("google_id", sa.String(255), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("google_id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "user_integrations",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("access_token", sa.Text(), nullable=False),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scopes", sa.Text(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_integration_user_id", "user_integrations", ["user_id"], unique=False)

    op.add_column("workspaces", sa.Column("created_by", sa.UUID(), nullable=True))
    op.create_foreign_key("fk_workspaces_created_by", "workspaces", "users", ["created_by"], ["id"], ondelete="SET NULL")

    op.add_column("clients", sa.Column("created_by", sa.UUID(), nullable=True))
    op.create_foreign_key("fk_clients_created_by", "clients", "users", ["created_by"], ["id"], ondelete="SET NULL")

    op.add_column("projects", sa.Column("created_by", sa.UUID(), nullable=True))
    op.create_foreign_key("fk_projects_created_by", "projects", "users", ["created_by"], ["id"], ondelete="SET NULL")

    op.add_column("meetings", sa.Column("created_by", sa.UUID(), nullable=True))
    op.create_foreign_key("fk_meetings_created_by", "meetings", "users", ["created_by"], ["id"], ondelete="SET NULL")


def downgrade() -> None:
    op.drop_constraint("fk_meetings_created_by", "meetings", type_="foreignkey")
    op.drop_column("meetings", "created_by")
    op.drop_constraint("fk_projects_created_by", "projects", type_="foreignkey")
    op.drop_column("projects", "created_by")
    op.drop_constraint("fk_clients_created_by", "clients", type_="foreignkey")
    op.drop_column("clients", "created_by")
    op.drop_constraint("fk_workspaces_created_by", "workspaces", type_="foreignkey")
    op.drop_column("workspaces", "created_by")
    op.drop_index("idx_integration_user_id", table_name="user_integrations")
    op.drop_table("user_integrations")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

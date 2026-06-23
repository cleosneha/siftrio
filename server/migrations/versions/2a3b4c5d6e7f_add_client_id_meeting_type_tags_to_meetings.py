"""add client_id meeting_type tags to meetings

Revision ID: 2a3b4c5d6e7f
Revises: 9549134024ab
Create Date: 2026-06-23 17:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "2a3b4c5d6e7f"
down_revision: Union[str, None] = "9549134024ab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("meetings_project_id_fkey", "meetings", type_="foreignkey")

    op.alter_column("meetings", "project_id", nullable=True)

    op.create_foreign_key(
        "meetings_project_id_fkey",
        "meetings",
        "projects",
        ["project_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column("meetings", sa.Column("client_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "meetings_client_id_fkey",
        "meetings",
        "clients",
        ["client_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.execute("""
        UPDATE meetings
        SET client_id = projects.client_id
        FROM projects
        WHERE meetings.project_id = projects.id
    """)

    op.alter_column("meetings", "client_id", nullable=False)

    op.execute("CREATE TYPE meetingtype AS ENUM ('PROJECT', 'MISCELLANEOUS')")

    op.add_column(
        "meetings",
        sa.Column(
            "meeting_type",
            postgresql.ENUM("PROJECT", "MISCELLANEOUS", name="meetingtype", create_type=False),
            nullable=False,
            server_default="PROJECT",
        ),
    )

    op.add_column(
        "meetings",
        sa.Column(
            "tags",
            postgresql.ARRAY(sa.Text()),
            nullable=False,
            server_default="{}",
        ),
    )

    op.create_index("idx_meeting_client_id", "meetings", ["client_id"])


def downgrade() -> None:
    op.drop_index("idx_meeting_client_id", table_name="meetings")
    op.drop_column("meetings", "tags")
    op.drop_column("meetings", "meeting_type")
    op.execute("DROP TYPE IF EXISTS meetingtype")
    op.drop_constraint("meetings_client_id_fkey", "meetings", type_="foreignkey")
    op.drop_column("meetings", "client_id")
    op.drop_constraint("meetings_project_id_fkey", "meetings", type_="foreignkey")
    op.alter_column("meetings", "project_id", nullable=False)
    op.create_foreign_key(
        "meetings_project_id_fkey",
        "meetings",
        "projects",
        ["project_id"],
        ["id"],
        ondelete="CASCADE",
    )

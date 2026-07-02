"""fix enum casing to uppercase

All other enums in this codebase use uppercase values (e.g., meetingtype -> 'PROJECT',
meetingprovider -> 'MANUAL') because SQLAlchemy sends Python enum member .name (uppercase)
for str, Enum subclasses.

Migration cd0a2d045956 accidentally created transcriptstatus and riskseverity with
lowercase values, causing: invalid input value for enum transcriptstatus: "PENDING"

Revision ID: e5f6a7b8c9d0
Revises: cd0a2d045956
Create Date: 2026-07-02 18:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, None] = 'cd0a2d045956'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- transcriptstatus: lowercase -> uppercase ---
    op.execute("ALTER TYPE transcriptstatus RENAME TO transcriptstatus_old")
    new_transcriptstatus = sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', name='transcriptstatus')
    new_transcriptstatus.create(op.get_bind())
    op.execute("""
        ALTER TABLE meetings
        ALTER COLUMN transcript_status
        TYPE transcriptstatus
        USING (
            CASE transcript_status::text
                WHEN 'pending' THEN 'PENDING'::transcriptstatus
                WHEN 'processing' THEN 'PROCESSING'::transcriptstatus
                WHEN 'completed' THEN 'COMPLETED'::transcriptstatus
                WHEN 'failed' THEN 'FAILED'::transcriptstatus
            END
        )
    """)
    op.execute("DROP TYPE IF EXISTS transcriptstatus_old")

    # --- riskseverity: lowercase -> uppercase ---
    op.execute("ALTER TYPE riskseverity RENAME TO riskseverity_old")
    new_riskseverity = sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='riskseverity')
    new_riskseverity.create(op.get_bind())
    op.execute("""
        ALTER TABLE risks
        ALTER COLUMN severity
        TYPE riskseverity
        USING (
            CASE severity::text
                WHEN 'low' THEN 'LOW'::riskseverity
                WHEN 'medium' THEN 'MEDIUM'::riskseverity
                WHEN 'high' THEN 'HIGH'::riskseverity
                WHEN 'critical' THEN 'CRITICAL'::riskseverity
            END
        )
    """)
    op.execute("DROP TYPE IF EXISTS riskseverity_old")


def downgrade() -> None:
    # --- riskseverity: uppercase -> lowercase ---
    op.execute("ALTER TYPE riskseverity RENAME TO riskseverity_old")
    old_riskseverity = sa.Enum('low', 'medium', 'high', 'critical', name='riskseverity')
    old_riskseverity.create(op.get_bind())
    op.execute("""
        ALTER TABLE risks
        ALTER COLUMN severity
        TYPE riskseverity
        USING (
            CASE severity::text
                WHEN 'LOW' THEN 'low'::riskseverity
                WHEN 'MEDIUM' THEN 'medium'::riskseverity
                WHEN 'HIGH' THEN 'high'::riskseverity
                WHEN 'CRITICAL' THEN 'critical'::riskseverity
            END
        )
    """)
    op.execute("DROP TYPE IF EXISTS riskseverity_old")

    # --- transcriptstatus: uppercase -> lowercase ---
    op.execute("ALTER TYPE transcriptstatus RENAME TO transcriptstatus_old")
    old_transcriptstatus = sa.Enum('pending', 'processing', 'completed', 'failed', name='transcriptstatus')
    old_transcriptstatus.create(op.get_bind())
    op.execute("""
        ALTER TABLE meetings
        ALTER COLUMN transcript_status
        TYPE transcriptstatus
        USING (
            CASE transcript_status::text
                WHEN 'PENDING' THEN 'pending'::transcriptstatus
                WHEN 'PROCESSING' THEN 'processing'::transcriptstatus
                WHEN 'COMPLETED' THEN 'completed'::transcriptstatus
                WHEN 'FAILED' THEN 'failed'::transcriptstatus
            END
        )
    """)
    op.execute("DROP TYPE IF EXISTS transcriptstatus_old")

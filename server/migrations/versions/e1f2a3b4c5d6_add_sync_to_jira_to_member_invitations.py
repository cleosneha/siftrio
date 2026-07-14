"""add_sync_to_jira_to_member_invitations

Revision ID: e1f2a3b4c5d6
Revises: cd0a2d045956
Create Date: 2026-07-13 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e1f2a3b4c5d6'
down_revision: Union[str, None] = 'd320b931a506'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'member_invitations',
        sa.Column('sync_to_jira', sa.Boolean(), nullable=False, server_default='false'),
    )


def downgrade() -> None:
    op.drop_column('member_invitations', 'sync_to_jira')

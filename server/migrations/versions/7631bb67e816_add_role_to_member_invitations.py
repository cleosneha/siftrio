"""add role to member_invitations

Revision ID: 7631bb67e816
Revises: d105dea6a3a7
Create Date: 2026-08-13 15:16:33.527148
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '7631bb67e816'
down_revision: Union[str, None] = 'd105dea6a3a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'member_invitations',
        sa.Column('role', sa.Enum('OWNER', 'ADMIN', 'MEMBER', 'VIEWER', name='memberrole'), server_default='MEMBER', nullable=False),
    )


def downgrade() -> None:
    op.drop_column('member_invitations', 'role')

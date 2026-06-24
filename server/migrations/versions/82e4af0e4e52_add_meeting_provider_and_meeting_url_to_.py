"""add meeting_provider and meeting_url to meetings

Revision ID: 82e4af0e4e52
Revises: 5e6f7a8b9c0d
Create Date: 2026-06-24 17:21:56.249985
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '82e4af0e4e52'
down_revision: Union[str, None] = '5e6f7a8b9c0d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE meetingprovider AS ENUM ('MANUAL', 'GOOGLE_MEET')")
    op.add_column('meetings', sa.Column('meeting_provider', sa.Enum('MANUAL', 'GOOGLE_MEET', name='meetingprovider', create_type=False), nullable=False, server_default='MANUAL'))
    op.add_column('meetings', sa.Column('meeting_url', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('meetings', 'meeting_url')
    op.drop_column('meetings', 'meeting_provider')
    op.execute('DROP TYPE IF EXISTS meetingprovider')

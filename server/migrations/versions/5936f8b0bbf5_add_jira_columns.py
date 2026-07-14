"""add_jira_columns

Revision ID: 5936f8b0bbf5
Revises: b4ea7b7c195c
Create Date: 2026-07-06 20:51:56.085660
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '5936f8b0bbf5'
down_revision: Union[str, None] = 'b4ea7b7c195c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('action_items', sa.Column('jira_issue_id', sa.String(length=255), nullable=True))
    op.add_column('action_items', sa.Column('jira_issue_key', sa.String(length=50), nullable=True))
    op.add_column('action_items', sa.Column('jira_issue_url', sa.Text(), nullable=True))
    op.add_column('action_items', sa.Column('jira_issue_type', sa.String(length=50), nullable=True))
    op.add_column('action_items', sa.Column('jira_synced_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('action_items', sa.Column('sync_status', sa.String(length=20), nullable=True))


def downgrade() -> None:
    op.drop_column('action_items', 'sync_status')
    op.drop_column('action_items', 'jira_synced_at')
    op.drop_column('action_items', 'jira_issue_type')
    op.drop_column('action_items', 'jira_issue_url')
    op.drop_column('action_items', 'jira_issue_key')
    op.drop_column('action_items', 'jira_issue_id')

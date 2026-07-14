"""latest_changes

Revision ID: cd0a2d045956
Revises: a1b2c3d4e5f6
Create Date: 2026-07-02 18:09:28.287042
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'cd0a2d045956'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    transcriptstatus_enum = sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', name='transcriptstatus')
    riskseverity_enum = sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='riskseverity')
    transcriptstatus_enum.create(op.get_bind(), checkfirst=True)
    riskseverity_enum.create(op.get_bind(), checkfirst=True)

    op.create_index(op.f('ix_clients_created_by'), 'clients', ['created_by'], unique=False)
    op.alter_column('meetings', 'transcript_status',
               existing_type=sa.VARCHAR(length=50),
               type_=transcriptstatus_enum,
               existing_nullable=True,
               postgresql_using='transcript_status::text::transcriptstatus')
    op.create_index('idx_meeting_fireflies_meeting_id', 'meetings', ['fireflies_meeting_id'], unique=False)
    op.create_index('idx_meeting_google_calendar_event_id', 'meetings', ['google_calendar_event_id'], unique=False)
    op.create_index('idx_meeting_google_meet_code', 'meetings', ['google_meet_code'], unique=False)
    op.create_index('idx_meeting_meeting_date', 'meetings', ['meeting_date'], unique=False)
    op.create_index(op.f('ix_meetings_created_by'), 'meetings', ['created_by'], unique=False)
    op.create_index(op.f('ix_projects_created_by'), 'projects', ['created_by'], unique=False)
    op.alter_column('risks', 'severity',
               existing_type=sa.VARCHAR(length=50),
               type_=riskseverity_enum,
               existing_nullable=True,
                postgresql_using='severity::text::riskseverity')
    op.create_unique_constraint('uq_user_integration_user_provider', 'user_integrations', ['user_id', 'provider'])
    op.create_index(op.f('ix_workspaces_created_by'), 'workspaces', ['created_by'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_workspaces_created_by'), table_name='workspaces')
    op.drop_constraint('uq_user_integration_user_provider', 'user_integrations', type_='unique')
    op.alter_column('risks', 'severity',
               existing_type=sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='riskseverity'),
               type_=sa.VARCHAR(length=50),
               existing_nullable=True)
    op.drop_index(op.f('ix_projects_created_by'), table_name='projects')
    op.drop_index(op.f('ix_meetings_created_by'), table_name='meetings')
    op.drop_index('idx_meeting_meeting_date', table_name='meetings')
    op.drop_index('idx_meeting_google_meet_code', table_name='meetings')
    op.drop_index('idx_meeting_google_calendar_event_id', table_name='meetings')
    op.drop_index('idx_meeting_fireflies_meeting_id', table_name='meetings')
    op.alter_column('meetings', 'transcript_status',
               existing_type=sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', name='transcriptstatus'),
               type_=sa.VARCHAR(length=50),
               existing_nullable=True)
    op.drop_index(op.f('ix_clients_created_by'), table_name='clients')

    riskseverity_enum = sa.Enum(name='riskseverity')
    riskseverity_enum.drop(op.get_bind(), checkfirst=True)
    transcriptstatus_enum = sa.Enum(name='transcriptstatus')
    transcriptstatus_enum.drop(op.get_bind(), checkfirst=True)

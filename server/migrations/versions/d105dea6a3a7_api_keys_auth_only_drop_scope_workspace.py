"""api keys auth only drop scope workspace

Revision ID: d105dea6a3a7
Revises: 0eeec470d827
Create Date: 2026-08-13 14:47:46.244919
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql

revision: str = 'd105dea6a3a7'
down_revision: Union[str, None] = '0eeec470d827'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('api_keys_workspace_id_fkey', 'api_keys', type_='foreignkey')
    op.drop_index(op.f('ix_api_keys_workspace_id'), table_name='api_keys')
    op.drop_column('api_keys', 'scope')
    op.drop_column('api_keys', 'workspace_id')
    sa.Enum(name='apikeyscope').drop(op.get_bind(), checkfirst=True)
    op.drop_index('idx_api_keys_active', table_name='api_keys', postgresql_where=sa.text('revoked_at IS NULL'))
    op.create_index(
        'idx_api_keys_active',
        'api_keys',
        ['user_id'],
        unique=True,
        postgresql_where=sa.text('revoked_at IS NULL'),
    )


def downgrade() -> None:
    op.drop_index('idx_api_keys_active', table_name='api_keys', postgresql_where=sa.text('revoked_at IS NULL'))
    op.create_index(
        'idx_api_keys_active',
        'api_keys',
        ['user_id'],
        unique=False,
        postgresql_where=sa.text('revoked_at IS NULL'),
    )
    sa.Enum('READ', 'WRITE', 'ADMIN', name='apikeyscope').create(op.get_bind(), checkfirst=True)
    op.add_column('api_keys', sa.Column('workspace_id', sa.UUID(), nullable=True))
    op.add_column('api_keys', sa.Column('scope', sa.Enum('READ', 'WRITE', 'ADMIN', name='apikeyscope'), server_default=sa.text("'READ'"), nullable=False))
    op.create_index(op.f('ix_api_keys_workspace_id'), 'api_keys', ['workspace_id'], unique=False)
    op.create_foreign_key(None, 'api_keys', 'workspaces', ['workspace_id'], ['id'], ondelete='SET NULL')

"""add ingestion_error column to meetings

Revision ID: 7190f0301d27
Revises: 47a48b6163cf
Create Date: 2026-07-29 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7190f0301d27"
down_revision: Union[str, None] = "47a48b6163cf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("meetings", sa.Column("ingestion_error", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("meetings", "ingestion_error")

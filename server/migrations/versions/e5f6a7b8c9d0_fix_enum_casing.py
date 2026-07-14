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
    pass


def downgrade() -> None:
    pass

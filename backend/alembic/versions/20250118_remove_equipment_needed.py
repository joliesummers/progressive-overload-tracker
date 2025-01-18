"""remove equipment_needed column

Revision ID: 20250118_remove_equipment_needed
Revises: 
Create Date: 2025-01-18 06:33:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250118_remove_equipment_needed'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the equipment_needed column
    op.drop_column('exercises', 'equipment_needed')


def downgrade() -> None:
    # Add back the equipment_needed column
    op.add_column('exercises', sa.Column('equipment_needed', sa.JSON(), nullable=True))

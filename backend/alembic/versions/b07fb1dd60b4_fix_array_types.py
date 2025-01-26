"""fix array types

Revision ID: b07fb1dd60b4
Revises: a07fb1dd60b4
Create Date: 2025-01-25 15:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY


# revision identifiers, used by Alembic.
revision = 'b07fb1dd60b4'
down_revision = 'a07fb1dd60b4'
branch_labels = None
depends_on = None


def upgrade():
    # Create temporary columns
    op.add_column('exercises', sa.Column('reps_array', ARRAY(sa.Integer()), nullable=True))
    op.add_column('exercises', sa.Column('weight_array', ARRAY(sa.Float()), nullable=True))
    
    # Copy data with conversion (will be NULL since JSON->ARRAY needs manual conversion)
    op.execute('UPDATE exercises SET reps_array = NULL, weight_array = NULL')
    
    # Drop old columns
    op.drop_column('exercises', 'reps')
    op.drop_column('exercises', 'weight')
    
    # Rename new columns
    op.alter_column('exercises', 'reps_array', new_column_name='reps')
    op.alter_column('exercises', 'weight_array', new_column_name='weight')


def downgrade():
    # Create temporary columns
    op.add_column('exercises', sa.Column('reps_json', sa.JSON(), nullable=True))
    op.add_column('exercises', sa.Column('weight_json', sa.JSON(), nullable=True))
    
    # Copy data with conversion (will be NULL since ARRAY->JSON needs manual conversion)
    op.execute('UPDATE exercises SET reps_json = NULL, weight_json = NULL')
    
    # Drop array columns
    op.drop_column('exercises', 'reps')
    op.drop_column('exercises', 'weight')
    
    # Rename JSON columns
    op.alter_column('exercises', 'reps_json', new_column_name='reps')
    op.alter_column('exercises', 'weight_json', new_column_name='weight')

"""change reps and weight to arrays

Revision ID: a07fb1dd60b4
Revises: f2a293209544
Create Date: 2025-01-25 15:53:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY


# revision identifiers, used by Alembic.
revision = 'a07fb1dd60b4'
down_revision = 'f2a293209544'
branch_labels = None
depends_on = None


def upgrade():
    # Drop old columns
    op.drop_column('exercises', 'reps')
    op.drop_column('exercises', 'weight')
    
    # Add new array columns
    op.add_column('exercises', sa.Column('reps', ARRAY(sa.Integer()), nullable=True))
    op.add_column('exercises', sa.Column('weight', ARRAY(sa.Float()), nullable=True))


def downgrade():
    # Drop array columns
    op.drop_column('exercises', 'reps')
    op.drop_column('exercises', 'weight')
    
    # Add back JSON columns
    op.add_column('exercises', sa.Column('reps', sa.JSON(), nullable=True))
    op.add_column('exercises', sa.Column('weight', sa.JSON(), nullable=True))

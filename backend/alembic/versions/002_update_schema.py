"""update schema

Revision ID: 002
Revises: 9a841c5c0d3b
Create Date: 2025-01-17 03:49:08.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON, ARRAY


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '9a841c5c0d3b'
branch_labels = None
depends_on = None


def upgrade():
    # Drop old foreign key from muscle_activations
    op.drop_constraint('muscle_activations_exercise_id_fkey', 'muscle_activations', type_='foreignkey')
    
    # Create exercise_muscle_association table
    op.create_table('exercise_muscle_association',
        sa.Column('exercise_id', sa.Integer(), nullable=False),
        sa.Column('muscle_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ),
        sa.ForeignKeyConstraint(['muscle_id'], ['muscle_activations.id'], ),
        sa.PrimaryKeyConstraint('exercise_id', 'muscle_id')
    )

    # Add new columns to exercises
    op.add_column('exercises', sa.Column('movement_pattern', sa.String(), nullable=True))
    op.add_column('exercises', sa.Column('reps', ARRAY(sa.Integer()), nullable=True))
    op.add_column('exercises', sa.Column('weight', ARRAY(sa.Float()), nullable=True))
    op.add_column('exercises', sa.Column('num_sets', sa.Integer(), nullable=True))
    op.add_column('exercises', sa.Column('rpe', sa.Float(), nullable=True))
    op.add_column('exercises', sa.Column('tempo', sa.String(), nullable=True))
    op.add_column('exercises', sa.Column('total_volume', sa.Float(), nullable=True))
    op.add_column('exercises', sa.Column('notes', sa.String(), nullable=True))
    op.add_column('exercises', sa.Column('equipment', sa.String(), nullable=True))
    op.add_column('exercises', sa.Column('difficulty', sa.String(), nullable=True))
    op.add_column('exercises', sa.Column('estimated_duration', sa.Integer(), nullable=True))
    op.add_column('exercises', sa.Column('rest_period', sa.Integer(), nullable=True))

    # Add new columns to muscle_activations
    op.add_column('muscle_activations', sa.Column('muscle_name', sa.String(), nullable=True))
    op.add_column('muscle_activations', sa.Column('activation_level', sa.String(), nullable=True))
    op.add_column('muscle_activations', sa.Column('estimated_volume', sa.Float(), nullable=True))


def downgrade():
    # Drop added columns from muscle_activations
    op.drop_column('muscle_activations', 'estimated_volume')
    op.drop_column('muscle_activations', 'activation_level')
    op.drop_column('muscle_activations', 'muscle_name')

    # Drop added columns from exercises
    op.drop_column('exercises', 'rest_period')
    op.drop_column('exercises', 'estimated_duration')
    op.drop_column('exercises', 'difficulty')
    op.drop_column('exercises', 'equipment')
    op.drop_column('exercises', 'notes')
    op.drop_column('exercises', 'total_volume')
    op.drop_column('exercises', 'tempo')
    op.drop_column('exercises', 'rpe')
    op.drop_column('exercises', 'num_sets')
    op.drop_column('exercises', 'weight')
    op.drop_column('exercises', 'reps')
    op.drop_column('exercises', 'movement_pattern')

    # Drop exercise_muscle_association table
    op.drop_table('exercise_muscle_association')

    # Recreate old foreign key
    op.create_foreign_key('muscle_activations_exercise_id_fkey', 'muscle_activations', 'exercises', ['exercise_id'], ['id'])

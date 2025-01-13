"""add workout tables

Revision ID: 001
Revises: 
Create Date: 2025-01-12 12:46:50.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create workout_sessions table
    op.create_table(
        'workout_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workout_sessions_id'), 'workout_sessions', ['id'], unique=False)

    # Create exercises table
    op.create_table(
        'exercises',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('movement_pattern', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['workout_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exercises_id'), 'exercises', ['id'], unique=False)

    # Create exercise_sets table
    op.create_table(
        'exercise_sets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('exercise_id', sa.Integer(), nullable=True),
        sa.Column('reps', sa.Integer(), nullable=True),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('set_number', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exercise_sets_id'), 'exercise_sets', ['id'], unique=False)

    # Create muscle_activations table
    op.create_table(
        'muscle_activations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('exercise_id', sa.Integer(), nullable=True),
        sa.Column('muscle_name', sa.String(), nullable=True),
        sa.Column('activation_level', sa.Enum('PRIMARY', 'SECONDARY', 'TERTIARY', name='activationlevel'), nullable=True),
        sa.Column('estimated_volume', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_muscle_activations_id'), 'muscle_activations', ['id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_muscle_activations_id'), table_name='muscle_activations')
    op.drop_table('muscle_activations')
    op.drop_index(op.f('ix_exercise_sets_id'), table_name='exercise_sets')
    op.drop_table('exercise_sets')
    op.drop_index(op.f('ix_exercises_id'), table_name='exercises')
    op.drop_table('exercises')
    op.drop_index(op.f('ix_workout_sessions_id'), table_name='workout_sessions')
    op.drop_table('workout_sessions')

"""update schema

Revision ID: 7db4b56c32de
Revises: 9a841c5c0d3b
Create Date: 2025-01-17 03:49:08.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7db4b56c32de'
down_revision = '9a841c5c0d3b'
branch_labels = None
depends_on = None


def upgrade():
    # Drop old foreign key and index from muscle_activations
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
    op.add_column('exercises', sa.Column('equipment_needed', sa.JSON(), nullable=True))
    op.add_column('exercises', sa.Column('notes', sa.String(), nullable=True))
    op.add_column('exercises', sa.Column('num_sets', sa.Integer(), nullable=True))
    op.add_column('exercises', sa.Column('reps', sa.Integer(), nullable=True))
    op.add_column('exercises', sa.Column('rpe', sa.Float(), nullable=True))
    op.add_column('exercises', sa.Column('tempo', sa.String(), nullable=True))

    # Add new columns to exercise_sets
    op.add_column('exercise_sets', sa.Column('sets', sa.Integer(), nullable=True))
    op.add_column('exercise_sets', sa.Column('rpe', sa.Float(), nullable=True))
    op.add_column('exercise_sets', sa.Column('tempo', sa.String(), nullable=True))
    op.add_column('exercise_sets', sa.Column('notes', sa.String(), nullable=True))

    # Add new columns to workout_sessions
    op.add_column('workout_sessions', sa.Column('sentiment_score', sa.Float(), nullable=True))
    op.add_column('workout_sessions', sa.Column('sentiment_analysis', sa.String(), nullable=True))
    op.add_column('workout_sessions', sa.Column('notes', sa.String(), nullable=True))

    # Create muscle_tracking table
    op.create_table('muscle_tracking',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('muscle_name', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('last_trained', sa.DateTime(), nullable=True),
        sa.Column('total_volume', sa.Float(), nullable=True),
        sa.Column('exercise_count', sa.Integer(), nullable=True),
        sa.Column('weekly_volume', sa.Float(), nullable=True),
        sa.Column('monthly_volume', sa.Float(), nullable=True),
        sa.Column('coverage_rating', sa.String(), nullable=True),
        sa.Column('recovery_status', sa.Float(), nullable=True),
        sa.Column('week_start', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_muscle_tracking_id'), 'muscle_tracking', ['id'], unique=False)
    op.create_index(op.f('ix_muscle_tracking_muscle_name'), 'muscle_tracking', ['muscle_name'], unique=False)

    # Create exercise_templates table
    op.create_table('exercise_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('muscle_involvement', sa.JSON(), nullable=True),
        sa.Column('equipment_needed', sa.JSON(), nullable=True),
        sa.Column('movement_pattern', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exercise_templates_id'), 'exercise_templates', ['id'], unique=False)
    op.create_index(op.f('ix_exercise_templates_name'), 'exercise_templates', ['name'], unique=True)

    # Create muscle_volume_data table
    op.create_table('muscle_volume_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('muscle_name', sa.String(), nullable=True),
        sa.Column('total_volume', sa.Float(), nullable=True),
        sa.Column('date', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_muscle_volume_data_id'), 'muscle_volume_data', ['id'], unique=False)
    op.create_index(op.f('ix_muscle_volume_data_muscle_name'), 'muscle_volume_data', ['muscle_name'], unique=False)


def downgrade():
    # Drop indices
    op.drop_index(op.f('ix_muscle_volume_data_muscle_name'), table_name='muscle_volume_data')
    op.drop_index(op.f('ix_muscle_volume_data_id'), table_name='muscle_volume_data')
    op.drop_index(op.f('ix_exercise_templates_name'), table_name='exercise_templates')
    op.drop_index(op.f('ix_exercise_templates_id'), table_name='exercise_templates')
    op.drop_index(op.f('ix_muscle_tracking_muscle_name'), table_name='muscle_tracking')
    op.drop_index(op.f('ix_muscle_tracking_id'), table_name='muscle_tracking')
    
    # Drop tables
    op.drop_table('muscle_volume_data')
    op.drop_table('exercise_templates')
    op.drop_table('muscle_tracking')
    op.drop_table('exercise_muscle_association')
    
    # Drop columns from workout_sessions if they exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('workout_sessions')]
    
    if 'sentiment_score' in columns:
        op.drop_column('workout_sessions', 'sentiment_score')
    if 'sentiment_analysis' in columns:
        op.drop_column('workout_sessions', 'sentiment_analysis')
    if 'notes' in columns:
        op.drop_column('workout_sessions', 'notes')

    # Drop columns from exercise_sets if they exist
    columns = [col['name'] for col in inspector.get_columns('exercise_sets')]
    if 'sets' in columns:
        op.drop_column('exercise_sets', 'sets')
    if 'rpe' in columns:
        op.drop_column('exercise_sets', 'rpe')
    if 'tempo' in columns:
        op.drop_column('exercise_sets', 'tempo')
    if 'notes' in columns:
        op.drop_column('exercise_sets', 'notes')

    # Drop columns from exercises if they exist
    columns = [col['name'] for col in inspector.get_columns('exercises')]
    if 'equipment_needed' in columns:
        op.drop_column('exercises', 'equipment_needed')
    if 'notes' in columns:
        op.drop_column('exercises', 'notes')
    if 'num_sets' in columns:
        op.drop_column('exercises', 'num_sets')
    if 'reps' in columns:
        op.drop_column('exercises', 'reps')
    if 'rpe' in columns:
        op.drop_column('exercises', 'rpe')
    if 'tempo' in columns:
        op.drop_column('exercises', 'tempo')

    # Add back the old foreign key to muscle_activations
    op.create_foreign_key('muscle_activations_exercise_id_fkey', 'muscle_activations', 'exercises', ['exercise_id'], ['id'])

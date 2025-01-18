from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Base
from app.models.exercise import Exercise, MuscleActivation, MuscleTracking, ExerciseTemplate, WorkoutSession, ExerciseSet, MuscleVolumeData
from app.core.settings import settings

def init_db():
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create a test user
        db.execute("INSERT INTO users (id, email) VALUES (1, 'test@example.com') ON CONFLICT DO NOTHING")
        
        # Create a test workout session
        db.execute("""
            INSERT INTO workout_sessions (
                id, user_id, start_time, end_time, 
                sentiment_score, sentiment_analysis, notes, total_volume
            )
            VALUES (
                1, 1, NOW() - INTERVAL '7 days', 
                NOW() - INTERVAL '7 days' + INTERVAL '1 hour',
                NULL, NULL, NULL, NULL
            )
            ON CONFLICT DO NOTHING
        """)
        
        # Create a test exercise
        db.execute("""
            INSERT INTO exercises (
                id, session_id, name, movement_pattern, 
                equipment_needed, notes, num_sets, reps, 
                weight, rpe, tempo
            )
            VALUES (
                1, 1, 'Bench Press', 'Push',
                '[]'::json, NULL, 3, 8,
                135.0, NULL, NULL
            )
            ON CONFLICT DO NOTHING
        """)
        
        db.commit()
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()

from app.models.database import Base, engine
from app.models.user import User
from app.models.exercise import Exercise, ExerciseSet, WorkoutSession, MuscleActivation
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from datetime import datetime, timedelta

def create_tables():
    # Create tables in the correct order
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create a test user
        db.execute(text("""
            INSERT INTO users (id, email, username) 
            VALUES (1, 'test@example.com', 'testuser') 
            ON CONFLICT DO NOTHING
        """))
        db.commit()
        
        # Create a test workout session
        db.execute(text("""
            INSERT INTO workout_sessions (id, user_id, start_time, end_time)
            VALUES (1, 1, NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days' + INTERVAL '1 hour')
            ON CONFLICT DO NOTHING
        """))
        db.commit()
        
        # Create a test exercise
        db.execute(text("""
            INSERT INTO exercises (id, session_id, name, movement_pattern, timestamp, total_volume)
            VALUES (1, 1, 'Bench Press', 'Push', NOW() - INTERVAL '7 days', 1080.0)
            ON CONFLICT DO NOTHING
        """))
        db.commit()

        # Create test exercise sets
        db.execute(text("""
            INSERT INTO exercise_sets (exercise_id, reps, weight, set_number)
            VALUES 
                (1, 8, 135.0, 1),
                (1, 8, 135.0, 2),
                (1, 8, 135.0, 3)
            ON CONFLICT DO NOTHING
        """))
        db.commit()
        
        print("Tables created and test data inserted successfully!")
    except Exception as e:
        print(f"Error setting up database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.database import Base
from app.core.settings import get_settings
import logging

logger = logging.getLogger(__name__)

def init_db():
    settings = get_settings()
    logger.info("Initializing database...")
    engine = create_engine(settings.database_url)
    Base.metadata.drop_all(bind=engine)  # Drop all tables to ensure clean state
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create a test user
        logger.info("Creating test user...")
        db.execute(
            text("INSERT INTO users (id, username, email) VALUES (1, 'testuser', 'test@example.com') ON CONFLICT DO NOTHING")
        )
        
        # Create a test workout session with auto-generated ID
        logger.info("Creating test workout session...")
        result = db.execute(
            text("""
                INSERT INTO workout_sessions (
                    user_id, start_time, end_time, 
                    total_volume
                )
                VALUES (
                    1, NOW() - INTERVAL '7 days', 
                    NOW() - INTERVAL '7 days' + INTERVAL '1 hour',
                    0
                )
                RETURNING id
            """)
        )
        session_id = result.scalar()
        
        # Create a test exercise with auto-generated ID
        logger.info("Creating test exercise...")
        db.execute(
            text("""
                INSERT INTO exercises (
                    session_id, name, movement_pattern, 
                    notes, num_sets, reps, weight, rpe,
                    tempo, total_volume, equipment, difficulty,
                    estimated_duration, rest_period
                )
                VALUES (
                    :session_id, 'Bench Press', 'Push',
                    'Test exercise', 3, '[8,8,8]', '[135,145,155]', 8,
                    '2-0-1', 3480, 'Barbell', 'Intermediate',
                    15, 90
                )
            """), {'session_id': session_id})
        
        db.commit()
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db()

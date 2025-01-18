import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.database import Base
from app.core.settings import settings

def setup_db():
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create a test user
        db.execute(text("INSERT INTO users (id, email) VALUES (1, 'test@example.com') ON CONFLICT DO NOTHING"))
        
        # Create a test workout session
        db.execute(text("""
            INSERT INTO workout_sessions (id, user_id, start_time, end_time)
            VALUES (1, 1, NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days' + INTERVAL '1 hour')
            ON CONFLICT DO NOTHING
        """))
        
        # Create a test exercise
        db.execute(text("""
            INSERT INTO exercises (id, session_id, name, movement_pattern, num_sets, reps, weight)
            VALUES (1, 1, 'Bench Press', 'Push', 3, 8, 135.0)
            ON CONFLICT DO NOTHING
        """))
        
        db.commit()
        print("Database setup completed successfully!")
    except Exception as e:
        print(f"Error setting up database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_db()

from .models.database import Base, engine
from .models.user import User
from .models.exercise import Exercise, ExerciseSet, WorkoutSession, MuscleActivation

def create_tables():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
    print("Tables created successfully!")

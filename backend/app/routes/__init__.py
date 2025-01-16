from .chat import router as chat_router
from .exercise import router as exercise_router
from .analytics import router as analytics_router
from .workout import router as workout_router

__all__ = [
    'chat_router',
    'exercise_router',
    'analytics_router',
    'workout_router',
]

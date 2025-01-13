from .chat import router as chat_router
from .exercise import router as exercise_router
from .analytics import router as analytics_router

__all__ = [
    'chat_router',
    'exercise_router',
    'analytics_router',
]

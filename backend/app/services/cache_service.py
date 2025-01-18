from typing import Any, Optional, Dict
import redis
import json
from datetime import timedelta
import logging
import os
from functools import wraps

logger = logging.getLogger(__name__)

class CacheService:
    """Service for handling caching of expensive computations"""
    
    def __init__(self):
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_client = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            decode_responses=True
        )
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None
            
    def set(self, key: str, value: Any, expiry: timedelta = timedelta(hours=1)):
        """Set value in cache with expiry"""
        try:
            self.redis_client.setex(
                key,
                expiry,
                json.dumps(value)
            )
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            
    def delete(self, key: str):
        """Delete value from cache"""
        try:
            self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            
    def generate_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from prefix and parameters"""
        # Sort kwargs to ensure consistent key generation
        sorted_items = sorted(kwargs.items())
        key_parts = [str(k) + str(v) for k, v in sorted_items]
        return f"{prefix}:{':'.join(key_parts)}"

def cached(prefix: str, ttl: timedelta = timedelta(hours=1)):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get cache service from first argument (self) if it exists
            cache_service = getattr(args[0], 'cache_service', None) if args else None
            if not cache_service:
                cache_service = CacheService()
                
            # Generate cache key
            cache_key = cache_service.generate_key(prefix, **kwargs)
            
            # Try to get from cache
            cached_value = cache_service.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value
                
            # Calculate value and cache it
            result = func(*args, **kwargs)
            cache_service.set(cache_key, result, ttl)
            logger.debug(f"Cache miss for {cache_key}, stored new value")
            return result
        return wrapper
    return decorator

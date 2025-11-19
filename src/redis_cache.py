"""
Redis Cache Manager
Provides caching layer for database queries
"""

import json
import redis
import pandas as pd
from typing import Optional, Any
from functools import wraps
from config import Config


class RedisCache:
    """Redis cache manager for database query results"""
    
    def __init__(self):
        """Initialize Redis connection"""
        self.enabled = Config.REDIS_ENABLED
        self.ttl = Config.REDIS_TTL
        self.client = None
        
        if self.enabled:
            try:
                self.client = redis.Redis(
                    host=Config.REDIS_HOST,
                    port=Config.REDIS_PORT,
                    db=Config.REDIS_DB,
                    password=Config.REDIS_PASSWORD if Config.REDIS_PASSWORD else None,
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                # Test connection
                self.client.ping()
                print(f"✓ Redis cache connected at {Config.REDIS_HOST}:{Config.REDIS_PORT}")
            except (redis.ConnectionError, redis.TimeoutError) as e:
                print(f"⚠ Redis connection failed: {e}. Caching disabled.")
                self.enabled = False
                self.client = None
        else:
            print("ℹ Redis caching is disabled")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled or not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis get error for key '{key}': {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        if not self.enabled or not self.client:
            return False
        
        try:
            ttl = ttl or self.ttl
            serialized = json.dumps(value)
            self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"Redis set error for key '{key}': {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled or not self.client:
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete error for key '{key}': {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.enabled or not self.client:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Redis delete pattern error for '{pattern}': {e}")
            return 0
    
    def flush_all(self) -> bool:
        """Flush all cache entries"""
        if not self.enabled or not self.client:
            return False
        
        try:
            self.client.flushdb()
            print("✓ Redis cache flushed")
            return True
        except Exception as e:
            print(f"Redis flush error: {e}")
            return False
    
    def cache_dataframe(self, key: str, df: pd.DataFrame, ttl: Optional[int] = None) -> bool:
        """Cache a pandas DataFrame"""
        if not self.enabled or not self.client:
            return False
        
        try:
            # Convert DataFrame to JSON
            data = {
                'data': df.to_dict(orient='records'),
                'columns': list(df.columns),
                'index': list(df.index)
            }
            return self.set(key, data, ttl)
        except Exception as e:
            print(f"Error caching DataFrame for key '{key}': {e}")
            return False
    
    def get_dataframe(self, key: str) -> Optional[pd.DataFrame]:
        """Retrieve cached DataFrame"""
        if not self.enabled or not self.client:
            return None
        
        try:
            data = self.get(key)
            if data and 'data' in data:
                return pd.DataFrame(data['data'], columns=data.get('columns'))
            return None
        except Exception as e:
            print(f"Error retrieving DataFrame for key '{key}': {e}")
            return None
    
    def invalidate_race_cache(self, race_id: Optional[int] = None):
        """Invalidate cache entries for a specific race or all races"""
        if race_id:
            pattern = f"race:{race_id}:*"
        else:
            pattern = "race:*"
        
        deleted = self.delete_pattern(pattern)
        if deleted > 0:
            print(f"✓ Invalidated {deleted} cache entries for pattern '{pattern}'")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.enabled or not self.client:
            return {'enabled': False}
        
        try:
            info = self.client.info('stats')
            return {
                'enabled': True,
                'total_connections_received': info.get('total_connections_received', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'used_memory_human': self.client.info('memory').get('used_memory_human', 'N/A')
            }
        except Exception as e:
            print(f"Error getting Redis stats: {e}")
            return {'enabled': True, 'error': str(e)}


def cache_query(key_prefix: str, ttl: Optional[int] = None):
    """
    Decorator to cache database query results
    
    Usage:
        @cache_query('races', ttl=3600)
        def get_all_races(self):
            # query logic
            return results
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Get or create cache instance
            if not hasattr(self, '_cache'):
                self._cache = RedisCache()
            
            # Generate cache key from function name and arguments
            args_str = ':'.join(str(arg) for arg in args if arg is not None)
            kwargs_str = ':'.join(f"{k}={v}" for k, v in sorted(kwargs.items()) if v is not None)
            cache_key_parts = [key_prefix, func.__name__]
            if args_str:
                cache_key_parts.append(args_str)
            if kwargs_str:
                cache_key_parts.append(kwargs_str)
            cache_key = ':'.join(cache_key_parts)
            
            # Try to get from cache
            cached_result = self._cache.get_dataframe(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(self, *args, **kwargs)
            if isinstance(result, pd.DataFrame):
                self._cache.cache_dataframe(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# Global cache instance
_cache_instance = None


def get_cache_instance() -> RedisCache:
    """Get global cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
    return _cache_instance
